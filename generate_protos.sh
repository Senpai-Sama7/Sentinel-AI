#!/bin/bash
# generate_protos.sh
# This script automates the generation of language-specific code from our .proto definitions.
# It should be run from the root of the monorepo.

# Exit immediately if a command exits with a non-zero status.
# Treat unset variables as an error.
# The return value of a pipeline is the status of the last command to exit with a non-zero status.
set -euo pipefail

# --- Prerequisite Checks ---
command -v protoc >/dev/null 2>&1 || { echo >&2 "ERROR: protoc not found. Please install the protobuf compiler."; exit 1; }
command -v protoc-gen-go >/dev/null 2>&1 || { echo >&2 "ERROR: protoc-gen-go not found. Run: go install google.golang.org/protobuf/cmd/protoc-gen-go@latest"; exit 1; }
command -v protoc-gen-go-grpc >/dev/null 2>&1 || { echo >&2 "ERROR: protoc-gen-go-grpc not found. Run: go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest"; exit 1; }
command -v poetry >/dev/null 2>&1 || { echo >&2 "ERROR: poetry not found. Please install poetry for Python dependency management."; exit 1; }

# --- Configuration ---
PROTO_DIR="./proto"
PYTHON_OUT_DIR="./orchestrator/models"
GO_OUT_DIR="./go_weaviate_proxy/pkg/proto"
RUST_OUT_DIR="./ast_parser/src/proto"
TS_OUT_DIR="./frontend/src/types/generated"

# --- Python Generation ---
echo "--> Generating Python Protobuf code..."
# Ensure the Python gRPC tools are installed within the poetry environment
(cd orchestrator && poetry install --only main)
mkdir -p "${PYTHON_OUT_DIR}"
(cd orchestrator && poetry run python -m grpc_tools.protoc \
    -I="../${PROTO_DIR}" \
    --python_out="${PYTHON_OUT_DIR}" \
    --grpc_python_out="${PYTHON_OUT_DIR}" \
    ../${PROTO_DIR}/ast_schemas.proto \
    ../${PROTO_DIR}/ast_service.proto)
# Create __init__.py files to make the generated directories Python packages
touch "${PYTHON_OUT_DIR}/__init__.py"
echo "✅ Python code generated in ${PYTHON_OUT_DIR}"

# --- Go Generation ---
echo "--> Generating Go Protobuf code..."
mkdir -p "${GO_OUT_DIR}"
protoc \
    -I="${PROTO_DIR}" \
    --go_out="${GO_OUT_DIR}" \
    --go_opt=paths=source_relative \
    --go-grpc_out="${GO_OUT_DIR}" \
    --go-grpc_opt=paths=source_relative \
    "${PROTO_DIR}/ast_schemas.proto" \
    "${PROTO_DIR}/ast_service.proto"
echo "✅ Go code generated in ${GO_OUT_DIR}"

# --- Rust Generation ---
echo "--> Generating Rust Protobuf code (via build.rs)..."
# Rust generation is handled by the `build.rs` script within the ast_parser crate
# when `cargo build` is run. We just ensure the output directory exists.
mkdir -p "${RUST_OUT_DIR}"
echo "✅ Rust output directory ensured at ${RUST_OUT_DIR}. Actual generation occurs during 'cargo build'."

# --- TypeScript Generation ---
# This requires `ts-protoc-gen` and `grpc-web` plugins
# npm install -g ts-protoc-gen
# npm install grpc-web
echo "--> Generating TypeScript Protobuf declarations..."
mkdir -p "${TS_OUT_DIR}"
# Note: This generates for grpc-web. For Node.js gRPC, you'd use a different plugin.
protoc \
    -I="${PROTO_DIR}" \
    --plugin="protoc-gen-ts=$(command -v protoc-gen-ts)" \
    --ts_out="service=grpc-web:${TS_OUT_DIR}" \
    --js_out="import_style=commonjs,binary:${TS_OUT_DIR}" \
    "${PROTO_DIR}/ast_schemas.proto" \
    "${PROTO_DIR}/ast_service.proto"
echo "✅ TypeScript code generated in ${TS_OUT_DIR}"

echo "-------------------------------------"
echo "🎉 Protobuf generation complete. 🎉"
echo "-------------------------------------"