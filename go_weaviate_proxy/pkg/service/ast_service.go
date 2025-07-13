package service

import (
	"context"
	"fmt"
	"log"

	pb "sentinel-codec/go_weaviate_proxy/pkg/proto"
	"sentinel-codec/go_weaviate_proxy/pkg/weaviate_client"

	"github.com/weaviate/weaviate/entities/models"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/anypb"
)

// ASTServiceServer implements the gRPC server for the ASTGraphService.
type ASTServiceServer struct {
	pb.UnimplementedASTGraphServiceServer
	WeaviateClient *weaviate_client.Client
}

// IngestAST handles the ingestion of AST nodes and their relationships.
func (s *ASTServiceServer) IngestAST(ctx context.Context, req *pb.IngestASTRequest) (*pb.IngestASTResponse, error) {
	log.Printf("Received IngestAST request with %d nodes and %d relationships", len(req.AstNodes), len(req.Relationships))

	if len(req.AstNodes) == 0 {
		return &pb.IngestASTResponse{Success: true, Message: "No nodes to ingest"}, nil
	}

	// 1. Convert Protobuf ASTNodes to Weaviate's models.Object
	weaviateObjects := make([]*models.Object, len(req.AstNodes))
	for i, node := range req.AstNodes {
		properties := map[string]interface{}{
			"nodeType":          node.NodeType,
			"startByte":         node.StartByte,
			"endByte":           node.EndByte,
			"startLine":         node.StartLine,
			"endLine":           node.EndLine,
			"sourceCodeSnippet": node.SourceCodeSnippet,
			"filePath":          node.FilePath,
			"gitCommitHash":     node.GitCommitHash,
			"name":              node.Name,
		}
		// Serialize the 'Any' proto to a base64 string for storage in Weaviate's text field.
		if node.Annotations != nil {
			serializedAnnotations, err := anypb.New(node.Annotations)
			if err == nil {
				properties["annotations"] = serializedAnnotations.String() // Simplified storage
			}
		}

		weaviateObjects[i] = &models.Object{
			Class:      "ASTNode",
			ID:         models.StrfmtUUID(node.Id),
			Properties: properties,
		}
	}

	// 2. Batch ingest the nodes
	err := s.WeaviateClient.BatchIngestNodes(ctx, weaviateObjects)
	if err != nil {
		log.Printf("Error during batch node ingestion: %v", err)
		return nil, status.Errorf(codes.Internal, "failed to ingest nodes: %v", err)
	}

	// 3. Batch create relationships (cross-references)
	for _, rel := range req.Relationships {
		err := s.WeaviateClient.Data().ReferenceCreator().
			WithClassName("ASTNode").
			WithID(rel.SourceNodeId).
			WithReferenceProperty(rel.RelationshipType).
			WithReference(s.WeaviateClient.Data().ReferencePayloadBuilder().
				WithClassName("ASTNode").
				WithID(rel.TargetNodeId).
				Payload()).
			Do(ctx)

		if err != nil {
			log.Printf("Error creating relationship from %s to %s: %v", rel.SourceNodeId, rel.TargetNodeId, err)
			return nil, status.Errorf(codes.Internal, "failed to create relationship: %v", err)
		}
	}

	log.Printf("Successfully ingested %d nodes and %d relationships", len(req.AstNodes), len(req.Relationships))

	ingestedIDs := make([]string, len(req.AstNodes))
	for i, node := range req.AstNodes {
		ingestedIDs[i] = node.Id
	}

	return &pb.IngestASTResponse{
		Success:         true,
		Message:         fmt.Sprintf("Successfully ingested %d nodes.", len(req.AstNodes)),
		IngestedNodeIds: ingestedIDs,
	}, nil
}

// GetASTNodes, UpdateASTNodes, DeleteASTNodes, TraverseGraph would be implemented here.
// They are stubbed out to keep this response focused, but would follow a similar pattern
// of converting gRPC requests to Weaviate queries and responses back to gRPC messages.