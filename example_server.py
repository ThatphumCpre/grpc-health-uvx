#!/usr/bin/env python3
"""
Example gRPC server with health check enabled.

This is a simple example server that you can use to test the health check tool.

Usage:
    python example_server.py
"""

import time
from concurrent import futures

import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc


def serve():
    """Start a simple gRPC server with health check enabled."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add health check service
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    
    # Set overall server health
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
    
    # Optionally set specific service health
    health_servicer.set("example.Service", health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set("example.AnotherService", health_pb2.HealthCheckResponse.NOT_SERVING)
    
    # Start server
    port = 50051
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    
    print(f"🚀 Example gRPC server started on port {port}")
    print(f"   Overall health: SERVING")
    print(f"   example.Service: SERVING")
    print(f"   example.AnotherService: NOT_SERVING")
    print(f"\nTest with:")
    print(f"   uvx --from . grpc-healthcheck --target localhost:{port}")
    print(f"   uvx --from . grpc-healthcheck --target localhost:{port} --service example.Service")
    print(f"   uvx --from . grpc-healthcheck --target localhost:{port} --service example.AnotherService")
    print(f"\nPress Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        server.stop(0)


if __name__ == "__main__":
    serve()

