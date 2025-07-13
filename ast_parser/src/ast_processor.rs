// ast_parser/src/ast_processor.rs

use tree_sitter::{Parser, Tree, Node, Language};
use std::collections::HashMap;
use tracing::{warn, error};
use uuid::Uuid;

use crate::proto_client::ast_schemas::{self, AstNode, NodeRelationship};

// External language functions from the tree-sitter crates
extern "C" {
    fn tree_sitter_python() -> Language;
    fn tree_sitter_javascript() -> Language;
    fn tree_sitter_rust() -> Language;
}

/// Determines the Tree-sitter language based on file extension.
fn get_language_from_path(file_path: &str) -> Option<Language> {
    match file_path.split('.').last() {
        Some("py") => Some(unsafe { tree_sitter_python() }),
        Some("js") | Some("jsx") => Some(unsafe { tree_sitter_javascript() }),
        Some("rs") => Some(unsafe { tree_sitter_rust() }),
        _ => None,
    }
}

/// Parses source code and transforms the AST into a flat list of Protobuf nodes and relationships.
pub fn parse_code_to_ast_nodes(
    code: &str,
    file_path: &str,
    git_commit_hash: &str,
) -> Option<(Vec<AstNode>, Vec<NodeRelationship>)> {
    let language = match get_language_from_path(file_path) {
        Some(lang) => lang,
        None => {
            warn!("Unsupported language for file: {}. Skipping.", file_path);
            return None;
        }
    };

    let mut parser = Parser::new();
    parser.set_language(language).ok()?;
    let tree = parser.parse(code, None)?;

    let mut nodes = Vec::new();
    let mut relationships = Vec::new();
    let mut id_map = HashMap::new();

    // Recursively traverse the tree
    traverse_recursive(
        tree.root_node(),
        code.as_bytes(),
        file_path,
        git_commit_hash,
        None,
        &mut nodes,
        &mut relationships,
        &mut id_map,
    );

    Some((nodes, relationships))
}

/// Recursive helper function to perform a depth-first traversal of the AST.
fn traverse_recursive(
    node: Node,
    source_bytes: &[u8],
    file_path: &str,
    git_commit_hash: &str,
    parent_uuid: Option<&str>,
    nodes: &mut Vec<AstNode>,
    relationships: &mut Vec<NodeRelationship>,
    id_map: &mut HashMap<usize, String>,
) {
    // Generate a new UUID for the current node.
    let current_uuid = Uuid::new_v4().to_string();
    id_map.insert(node.id(), current_uuid.clone());

    // Extract the source code snippet for this node.
    let snippet = node.utf8_text(source_bytes).unwrap_or("").to_string();

    // Extract an identifiable name if possible (e.g., function name, variable name).
    let name = node.child_by_field_name("name")
        .and_then(|n| n.utf8_text(source_bytes).ok())
        .unwrap_or("")
        .to_string();

    // Create the Protobuf ASTNode object.
    nodes.push(AstNode {
        id: current_uuid.clone(),
        node_type: node.kind().to_string(),
        source_code_snippet: snippet,
        file_path: file_path.to_string(),
        git_commit_hash: git_commit_hash.to_string(),
        name,
        start_byte: node.start_byte() as i32,
        end_byte: node.end_byte() as i32,
        start_line: node.start_position().row as i32,
        end_line: node.end_position().row as i32,
        annotations: None, // Annotations would be added in a later processing step.
    });

    // If there's a parent, create the "hasChild" relationship.
    if let Some(p_uuid) = parent_uuid {
        relationships.push(NodeRelationship {
            source_node_id: p_uuid.to_string(),
            target_node_id: current_uuid.clone(),
            relationship_type: "hasChild".to_string(),
        });
    }

    // Recurse into children.
    let mut cursor = node.walk();
    for child in node.children(&mut cursor) {
        traverse_recursive(
            child,
            source_bytes,
            file_path,
            git_commit_hash,
            Some(&current_uuid),
            nodes,
            relationships,
            id_map,
        );
    }
}