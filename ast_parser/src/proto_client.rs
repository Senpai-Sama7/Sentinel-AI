// ast_parser/src/proto_client.rs

// This includes the generated code from build.rs
pub mod ast_schemas {
    tonic::include_proto!("ast_schemas");
}
pub mod ast_service {
    tonic::include_proto!("ast_service");
}

use tonic::transport::Channel;
use tracing::info;

// Re-export clients for easy use in other modules
pub use ast_service::ast_graph_service_client::AstGraphServiceClient;
pub use ast_service::wasm_validation_service_client::WasmValidationServiceClient;

pub struct ASTGraphClient {
    pub client: AstGraphServiceClient<Channel>,
}

impl ASTGraphClient {
    pub async fn new(addr: &str) -> Result<Self, Box<dyn std::error::Error>> {
        info!("Connecting to ASTGraphService at: {}", addr);
        let client = AstGraphServiceClient::connect(addr.to_string()).await?;
        info!("Successfully connected to ASTGraphService.");
        Ok(Self { client })
    }

    pub async fn ingest_ast(
        &mut self,
        request: ast_service::IngestASTRequest,
    ) -> Result<ast_schemas::IngestASTResponse, tonic::Status> {
        let response = self.client.ingest_ast(request).await?.into_inner();
        Ok(response)
    }
}