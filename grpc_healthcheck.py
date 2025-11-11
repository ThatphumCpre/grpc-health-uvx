#!/usr/bin/env python3
"""
gRPC Health Check Tool

A simple tool to perform health checks on gRPC servers using the standard
gRPC Health Checking Protocol (grpc.health.v1).

Usage:
    uvx --from . grpc-healthcheck --host localhost --port 50051
    uvx --from . grpc-healthcheck --target localhost:50051 --service myservice
"""

import argparse
import sys
from typing import Optional

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc


class HealthCheckError(Exception):
    """Custom exception for health check failures."""
    pass


def check_health(
    target: str,
    service: str = "",
    timeout: float = 5.0,
    use_tls: bool = False,
    verbose: bool = False
) -> bool:
    """
    Perform a health check against a gRPC server.
    
    Args:
        target: The server address (e.g., "localhost:50051")
        service: The service name to check (empty string for overall server health)
        timeout: Timeout in seconds for the health check
        use_tls: Whether to use TLS/SSL for the connection
        verbose: Whether to print verbose output
        
    Returns:
        True if the service is SERVING, False otherwise
        
    Raises:
        HealthCheckError: If the health check fails
    """
    if verbose:
        print(f"🔍 Checking health of gRPC server at {target}")
        if service:
            print(f"   Service: {service}")
        else:
            print(f"   Service: <overall server health>")
        print(f"   Timeout: {timeout}s")
        print(f"   TLS: {'enabled' if use_tls else 'disabled'}")
        print()

    # Create the appropriate channel
    if use_tls:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(target, credentials)
    else:
        channel = grpc.insecure_channel(target)

    try:
        # Create a health check stub
        stub = health_pb2_grpc.HealthStub(channel)
        
        # Create the health check request
        request = health_pb2.HealthCheckRequest(service=service)
        
        # Perform the health check
        try:
            response = stub.Check(request, timeout=timeout)
        except grpc.RpcError as e:
            status_code = e.code()
            details = e.details()
            
            if verbose:
                print(f"❌ gRPC Error: {status_code.name}")
                print(f"   Details: {details}")
            
            if status_code == grpc.StatusCode.UNIMPLEMENTED:
                raise HealthCheckError(
                    "Health check not implemented on the server. "
                    "Make sure the server implements grpc.health.v1.Health service."
                )
            elif status_code == grpc.StatusCode.DEADLINE_EXCEEDED:
                raise HealthCheckError(f"Health check timed out after {timeout}s")
            elif status_code == grpc.StatusCode.UNAVAILABLE:
                raise HealthCheckError(f"Cannot connect to {target}")
            elif status_code == grpc.StatusCode.NOT_FOUND:
                raise HealthCheckError(f"Service '{service}' not found")
            else:
                raise HealthCheckError(f"Health check failed: {status_code.name} - {details}")
        
        # Check the response status
        status = response.status
        status_name = health_pb2.HealthCheckResponse.ServingStatus.Name(status)
        
        if verbose:
            if status == health_pb2.HealthCheckResponse.SERVING:
                print(f"✅ Service is {status_name}")
            elif status == health_pb2.HealthCheckResponse.NOT_SERVING:
                print(f"❌ Service is {status_name}")
            elif status == health_pb2.HealthCheckResponse.UNKNOWN:
                print(f"⚠️  Service status is {status_name}")
            else:
                print(f"❓ Service status: {status_name}")
        
        return status == health_pb2.HealthCheckResponse.SERVING
        
    finally:
        channel.close()


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="gRPC Health Check Tool - Check the health of gRPC services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check overall server health
  %(prog)s --target localhost:50051
  
  # Check specific service
  %(prog)s --target localhost:50051 --service myapp.UserService
  
  # Using separate host and port
  %(prog)s --host localhost --port 50051
  
  # With TLS and custom timeout
  %(prog)s --target example.com:443 --tls --timeout 10
  
  # Verbose output
  %(prog)s --target localhost:50051 -v
        """
    )
    
    # Connection options
    conn_group = parser.add_mutually_exclusive_group(required=True)
    conn_group.add_argument(
        "--target",
        help="gRPC server target address (e.g., 'localhost:50051')"
    )
    conn_group.add_argument(
        "--host",
        help="gRPC server host (use with --port)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        help="gRPC server port (use with --host)"
    )
    
    # Health check options
    parser.add_argument(
        "--service",
        default="",
        help="Service name to check (empty for overall server health)"
    )
    
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout in seconds (default: 5.0)"
    )
    
    parser.add_argument(
        "--tls",
        action="store_true",
        help="Use TLS/SSL for the connection"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Build target address
    if args.target:
        target = args.target
    else:
        if args.port is None:
            parser.error("--port is required when using --host")
        target = f"{args.host}:{args.port}"
    
    # Perform the health check
    try:
        is_healthy = check_health(
            target=target,
            service=args.service,
            timeout=args.timeout,
            use_tls=args.tls,
            verbose=args.verbose
        )
        
        if is_healthy:
            if not args.verbose:
                print(f"✅ Service is healthy")
            sys.exit(0)
        else:
            if not args.verbose:
                print(f"❌ Service is not healthy")
            sys.exit(1)
            
    except HealthCheckError as e:
        print(f"❌ Health check failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

