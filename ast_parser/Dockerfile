# Dockerfile for the Rust ast_parser service

# --- Stage 1: Builder ---
# This stage compiles the Rust application and its dependencies.
FROM rust:1.77-slim-bookworm as builder

WORKDIR /app

# Install build essentials and protoc
RUN apt-get update && apt-get install -y build-essential protobuf-compiler

# Copy the entire project context
COPY . .

# Build the application in release mode for performance.
RUN cargo build --release

# --- Stage 2: Final Production Image ---
# This stage creates a minimal image with only the compiled binary.
FROM debian:bookworm-slim

# Set the working directory
WORKDIR /app

# Copy the compiled binary from the builder stage.
COPY --from=builder /app/target/release/ast_parser .

# The application binary is the only thing needed to run.
# The container is minimal and secure.
EXPOSE 50051 # Expose the gRPC port if this service were to become a server

# The command to run the application.
# In a real scenario, this might be a long-running process that watches a message queue.
# For this example, it runs once and exits.
CMD ["./ast_parser"]