# Dockerfile

# --- Stage 1: Builder ---
# Use a specific Go version for reproducible builds.
FROM golang:1.22-alpine AS builder

# Set the working directory inside the container.
WORKDIR /app

# Copy go.mod and go.sum files to leverage Docker's layer caching.
# Dependencies are downloaded only when these files change.
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of the application source code.
COPY . .

# Build the application into a static binary.
# CGO_ENABLED=0 disables Cgo, creating a static binary without system dependencies.
# -ldflags="-w -s" strips debug information, reducing the binary size.
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o /go_weaviate_proxy .

# --- Stage 2: Final Production Image ---
# Use the 'scratch' image, which is an empty image. This is the most secure
# and minimal base possible, containing only our compiled binary.
FROM scratch

# Set the working directory.
WORKDIR /

# Copy the compiled binary from the builder stage.
COPY --from=builder /go_weaviate_proxy .

# Copy CA certificates if your service needs to make outbound TLS calls.
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Expose the gRPC port.
EXPOSE 50052

# The command to run the application.
CMD ["/go_weaviate_proxy"]