mod ast_processor;
mod proto_client;

use std::env;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use tokio::fs;
use tracing::{info, error, Level};
use tracing_subscriber::{FmtSubscriber, EnvFilter};
use rayon::prelude::*;
use futures::stream::{self, StreamExt};

use proto_client::{ASTGraphClient, ast_schemas::{self, AstNode, NodeRelationship}};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let subscriber = FmtSubscriber::builder()
        .with_env_filter(EnvFilter::from_default_env().with_default_directive(Level::INFO.into()))
        .finish();
    tracing::subscriber::set_global_default(subscriber)?;

    info!("Starting AST Parser service...");

    let go_proxy_grpc_addr = env::var("GO_PROXY_GRPC_ADDR").unwrap_or_else(|_| "http://[::1]:50052".to_string());
    let repo_path_str = env::var("GIT_REPO_PATH").unwrap_or_else(|_| "./sample_repo".to_string());

    let repo_path = PathBuf::from(repo_path_str);
    if !repo_path.exists() || !repo_path.is_dir() {
        error!("Git repository path does not exist or is not a directory: {:?}", repo_path);
        return Err("Invalid GIT_REPO_PATH".into());
    }

    let mut ast_graph_client = ASTGraphClient::new(&go_proxy_grpc_addr).await?;

    info!("Scanning repository at: {:?}", repo_path);
    // In a real system, you'd use git2 to get the HEAD commit hash.
    let current_commit_hash = "mock-commit-hash-12345";

    let mut paths_to_process = Vec::new();
    let mut read_dir = fs::read_dir(&repo_path).await?;
    while let Some(entry) = read_dir.next_entry().await? {
        let path = entry.path();
        if path.is_file() {
            paths_to_process.push(path);
        }
    }

    info!("Found {} files to process.", paths_to_process.len());

    let all_nodes = Arc::new(Mutex::new(Vec::new()));
    let all_relationships = Arc::new(Mutex::new(Vec::new()));

    let processing_futures = stream::iter(paths_to_process)
        .map(|path| {
            let all_nodes = Arc::clone(&all_nodes);
            let all_relationships = Arc::clone(&all_relationships);
            let repo_path_clone = repo_path.clone();

            tokio::spawn(async move {
                if let Ok(content) = fs::read_to_string(&path).await {
                    let file_path_str = path.strip_prefix(&repo_path_clone).unwrap_or(&path).to_string_lossy().to_string();

                    // Offload the CPU-intensive parsing to a blocking thread pool
                    let result = tokio::task::spawn_blocking(move || {
                        ast_processor::parse_code_to_ast_nodes(&content, &file_path_str, current_commit_hash)
                    }).await.unwrap();

                    if let Some((nodes, relationships)) = result {
                        all_nodes.lock().unwrap().extend(nodes);
                        all_relationships.lock().unwrap().extend(relationships);
                    }
                }
            })
        })
        .buffer_unordered(num_cpus::get()) // Process files in parallel, limited by CPU count
        .collect::<Vec<_>>();

    processing_futures.await;

    let final_nodes = all_nodes.lock().unwrap().drain(..).collect::<Vec<_>>();
    let final_relationships = all_relationships.lock().unwrap().drain(..).collect::<Vec<_>>();

    if !final_nodes.is_empty() {
        info!("Ingesting {} AST nodes and {} relationships into Weaviate...", final_nodes.len(), final_relationships.len());
        let request = ast_schemas::IngestASTRequest {
            ast_nodes: final_nodes,
            relationships: final_relationships,
        };
        match ast_graph_client.ingest_ast(request).await {
            Ok(resp) => info!("Ingestion successful: {}", resp.message),
            Err(e) => error!("Ingestion failed: {}", e),
        }
    } else {
        info!("No new nodes to ingest.");
    }

    info!("AST Parser service finished its run.");
    Ok(())
}
