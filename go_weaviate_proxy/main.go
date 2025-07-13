package main

import (
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"

	pb "sentinel-codec/go_weaviate_proxy/pkg/proto"
	"sentinel-codec/go_weaviate_proxy/pkg/service"
	"sentinel-codec/go_weaviate_proxy/pkg/weaviate_client"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

func main() {
	log.Println("Starting Go Weaviate gRPC Proxy...")

	// --- Configuration ---
	grpcPort := os.Getenv("GRPC_PORT")
	if grpcPort == "" {
		grpcPort = "50052"
	}
	listenAddr := fmt.Sprintf(":%s", grpcPort)

	// --- Initialize Dependencies ---
	weaviateClient, err := weaviate_client.New()
	if err != nil {
		log.Fatalf("FATAL: Failed to create Weaviate client: %v", err)
	}

	// --- Setup gRPC Server ---
	lis, err := net.Listen("tcp", listenAddr)
	if err != nil {
		log.Fatalf("FATAL: Failed to listen on %s: %v", listenAddr, err)
	}

	grpcServer := grpc.NewServer()

	// Register our service implementation
	astServiceServer := &service.ASTServiceServer{
		WeaviateClient: weaviateClient,
	}
	pb.RegisterASTGraphServiceServer(grpcServer, astServiceServer)

	// Register reflection service for debugging with tools like grpcurl
	reflection.Register(grpcServer)

	// --- Start Server and Handle Graceful Shutdown ---
	go func() {
		log.Printf("gRPC server listening at %v", lis.Addr())
		if err := grpcServer.Serve(lis); err != nil {
			log.Fatalf("FATAL: Failed to serve gRPC: %v", err)
		}
	}()

	// Wait for termination signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down gRPC server...")
	grpcServer.GracefulStop()
	log.Println("gRPC server stopped.")
}