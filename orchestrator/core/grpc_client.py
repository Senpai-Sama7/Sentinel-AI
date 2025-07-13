# orchestrator/core/grpc_client.py
import grpc
import asyncio
import logging
from typing import Optional

from orchestrator.core.config import GO_PROXY_GRPC_ADDR
from orchestrator.models import ast_service_pb2_grpc, ast_schemas_pb2

class GrpcClient:
    """A robust, singleton gRPC client for the Go Weaviate Proxy."""
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GrpcClient, cls).__new__(cls)
            cls._instance.channel: Optional[grpc.aio.Channel] = None
            cls._instance.ast_stub: Optional[ast_service_pb2_grpc.ASTGraphServiceStub] = None
        return cls._instance

    async def connect(self):
        async with self._lock:
            if self.channel is None:
                logging.info(f"Connecting to gRPC server at {GO_PROXY_GRPC_ADDR}...")
                try:
                    self.channel = grpc.aio.insecure_channel(GO_PROXY_GRPC_ADDR)
                    await asyncio.wait_for(self.channel.channel_ready(), timeout=10.0)
                    self.ast_stub = ast_service_pb2_grpc.ASTGraphServiceStub(self.channel)
                    logging.info("gRPC connection successful.")
                except (asyncio.TimeoutError, grpc.aio.AioRpcError) as e:
                    self.channel = None
                    raise ConnectionError(f"gRPC connection failed: {e}")

    async def close(self):
        async with self._lock:
            if self.channel:
                await self.channel.close()
                self.channel = None
                self.ast_stub = None
                logging.info("gRPC connection closed.")

    def get_ast_stub(self) -> ast_service_pb2_grpc.ASTGraphServiceStub:
        if not self.ast_stub:
            raise ConnectionError("gRPC client not connected.")
        return self.ast_stub

grpc_client = GrpcClient()