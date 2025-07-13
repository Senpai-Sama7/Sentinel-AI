package weaviate_client

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/weaviate/weaviate-go-client/v4/weaviate"
	"github.com/weaviate/weaviate/entities/models"
)

// Client wraps the Weaviate Go client to provide a simplified interface and startup resilience.
type Client struct {
	*weaviate.Client
}

// New creates and configures a new Weaviate client with a readiness check.
func New() (*Client, error) {
	weaviateHost := os.Getenv("WEAVIATE_HOST")
	if weaviateHost == "" {
		weaviateHost = "localhost"
	}
	weaviatePort := os.Getenv("WEAVIATE_PORT")
	if weaviatePort == "" {
		weaviatePort = "8080"
	}

	cfg := weaviate.Config{
		Host:   fmt.Sprintf("%s:%s", weaviateHost, weaviatePort),
		Scheme: "http",
	}

	client, err := weaviate.NewClient(cfg)
	if err != nil {
		return nil, fmt.Errorf("could not create weaviate client: %w", err)
	}

	// Retry loop to wait for Weaviate to be ready. Essential for containerized environments.
	maxRetries := 5
	retryDelay := 5 * time.Second
	for i := 0; i < maxRetries; i++ {
		isReady, _ := client.Misc().ReadyChecker().Do(context.Background())
		if isReady {
			log.Println("Successfully connected to Weaviate.")
			return &Client{client}, nil
		}
		log.Printf("Weaviate not ready, retrying in %v... (%d/%d)", retryDelay, i+1, maxRetries)
		time.Sleep(retryDelay)
	}

	return nil, fmt.Errorf("weaviate not ready after %d retries", maxRetries)
}

// BatchIngestNodes performs a high-throughput batch ingestion of ASTNode objects.
func (c *Client) BatchIngestNodes(ctx context.Context, nodes []*models.Object) error {
	batcher := c.Batch().ObjectsBatcher()
	for _, node := range nodes {
		batcher.WithObjects(node)
	}

	resp, err := batcher.Do(ctx)
	if err != nil {
		return fmt.Errorf("batch ingestion failed: %w", err)
	}

	// Check for individual errors within the batch response
	for _, res := range resp {
		if res.Result != nil && res.Result.Errors != nil {
			// In a real system, you might collect all errors, but failing on the first is safer.
			return fmt.Errorf("error during batch ingestion for object %s: %v", res.ID, res.Result.Errors.Error[0].Message)
		}
	}

	return nil
}