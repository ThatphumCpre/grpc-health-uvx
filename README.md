# gRPC Health Check Tool

A simple and powerful CLI tool to perform health checks on gRPC servers using the standard [gRPC Health Checking Protocol](https://github.com/grpc/grpc/blob/master/doc/health-checking.md) (grpc.health.v1).

## Features

- ✅ **Zero Installation** - Run directly with `uvx` without installing
- 🔒 **TLS/SSL Support** - Check secure gRPC endpoints
- ⏱️ **Configurable Timeout** - Set custom timeout values
- 🎯 **Service-Specific Checks** - Check individual services or overall server health
- 📊 **Verbose Mode** - Detailed output for debugging
- 🚀 **CI/CD Ready** - Exit codes perfect for automation
- 🐳 **Docker & Kubernetes Compatible** - Use in health probes

## Quick Start

### Run with uvx (Recommended)

No installation needed! Just run:

```bash
# Check overall server health
uvx --from git+https://github.com/ThatphumCpre/grpc-health-uvx grpc-healthcheck --target localhost:50051

# Short version after first run (cached)
uvx grpc-healthcheck@git+https://github.com/ThatphumCpre/grpc-health-uvx --target localhost:50051
```

### Install with pip/uv

```bash
# Using uv
uv pip install git+https://github.com/ThatphumCpre/grpc-health-uvx

# Using pip
pip install git+https://github.com/ThatphumCpre/grpc-health-uvx

# Run after installation
grpc-healthcheck --target localhost:50051
```

### Run from Local Clone

```bash
# Clone the repository
git clone https://github.com/ThatphumCpre/grpc-health-uvx
cd grpc-health-uvx

# Run with uvx
uvx --from . grpc-healthcheck --target localhost:50051
```

## Usage

### Basic Usage

```bash
# Check overall server health
uvx --from git+https://github.com/ThatphumCpre/grpc-health-uvx grpc-healthcheck --target localhost:50051

# Check specific service
uvx --from git+https://github.com/ThatphumCpre/grpc-health-uvx grpc-healthcheck \
  --target localhost:50051 \
  --service myapp.UserService

# Using separate host and port
grpc-healthcheck --host localhost --port 50051
```

### Advanced Options

```bash
# Verbose mode for detailed output
grpc-healthcheck --target localhost:50051 -v

# Use TLS/SSL
grpc-healthcheck --target secure.example.com:443 --tls

# Custom timeout (default: 5 seconds)
grpc-healthcheck --target localhost:50051 --timeout 10

# All options combined
grpc-healthcheck \
  --target secure.example.com:443 \
  --service myapp.UserService \
  --tls \
  --timeout 10 \
  -v
```

### CLI Options

```
--target TARGET        gRPC server address (e.g., 'localhost:50051')
--host HOST           gRPC server host (use with --port)
--port PORT           gRPC server port (use with --host)
--service SERVICE     Service name to check (empty for overall server health)
--timeout TIMEOUT     Timeout in seconds (default: 5.0)
--tls                 Use TLS/SSL for the connection
-v, --verbose         Enable verbose output
-h, --help            Show help message
```

## Exit Codes

- `0`: Service is healthy (SERVING)
- `1`: Service is unhealthy (NOT_SERVING, UNKNOWN, or error occurred)

Perfect for use in scripts, CI/CD pipelines, and monitoring systems.

## Integration Examples

### Shell Script

```bash
#!/bin/bash

# Wait for gRPC server to be ready
if uvx grpc-healthcheck@git+https://github.com/ThatphumCpre/grpc-health-uvx \
   --target localhost:50051; then
    echo "Server is ready!"
else
    echo "Server is not ready"
    exit 1
fi
```

### Docker Health Check

```dockerfile
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Your gRPC server setup
COPY . /app
WORKDIR /app

# Health check using uvx
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD uvx grpc-healthcheck@git+https://github.com/ThatphumCpre/grpc-health-uvx \
        --target localhost:50051 || exit 1

CMD ["python", "server.py"]
```

### Kubernetes Liveness/Readiness Probe

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: grpc-server
spec:
  containers:
  - name: server
    image: your-grpc-server:latest
    ports:
    - containerPort: 50051
      name: grpc
    
    # Liveness probe - check if server is alive
    livenessProbe:
      exec:
        command:
        - uvx
        - grpc-healthcheck@git+https://github.com/ThatphumCpre/grpc-health-uvx
        - --target
        - localhost:50051
      initialDelaySeconds: 10
      periodSeconds: 15
      timeoutSeconds: 5
      failureThreshold: 3
    
    # Readiness probe - check if server is ready to serve traffic
    readinessProbe:
      exec:
        command:
        - uvx
        - grpc-healthcheck@git+https://github.com/ThatphumCpre/grpc-health-uvx
        - --target
        - localhost:50051
        - --service
        - myapp.UserService
      initialDelaySeconds: 5
      periodSeconds: 10
      timeoutSeconds: 5
```

### CI/CD Integration

**GitHub Actions:**

```yaml
name: Test gRPC Service
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Start gRPC server
        run: |
          docker-compose up -d grpc-server
      
      - name: Wait for gRPC server
        run: |
          for i in {1..30}; do
            if uvx grpc-healthcheck@git+https://github.com/ThatphumCpre/grpc-health-uvx \
               --target localhost:50051; then
              echo "✅ Server is ready!"
              exit 0
            fi
            echo "⏳ Waiting for server... ($i/30)"
            sleep 2
          done
          echo "❌ Server failed to start"
          exit 1
      
      - name: Run tests
        run: |
          # Your tests here
          npm test
```

**GitLab CI:**

```yaml
test:
  stage: test
  script:
    - docker-compose up -d grpc-server
    - |
      for i in $(seq 1 30); do
        if uvx grpc-healthcheck@git+https://github.com/ThatphumCpre/grpc-health-uvx \
           --target localhost:50051; then
          echo "Server is ready!"
          break
        fi
        sleep 2
      done
    - npm test
```

## Requirements

- Python 3.8+
- grpcio >= 1.60.0
- grpcio-health-checking >= 1.60.0

## gRPC Health Checking Protocol

This tool implements the standard [gRPC Health Checking Protocol](https://github.com/grpc/grpc/blob/master/doc/health-checking.md) (grpc.health.v1).

Your gRPC server must implement the `grpc.health.v1.Health` service for health checks to work.

### Adding Health Check to Your gRPC Server

#### Python Server

```python
from concurrent import futures
import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add your services
    # YourService_pb2_grpc.add_YourServiceServicer_to_server(YourServicer(), server)
    
    # Add health check service
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    
    # Set health status
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)  # Overall server health
    health_servicer.set("myapp.UserService", health_pb2.HealthCheckResponse.SERVING)
    
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

#### Go Server

```go
package main

import (
    "net"
    "google.golang.org/grpc"
    "google.golang.org/grpc/health"
    "google.golang.org/grpc/health/grpc_health_v1"
)

func main() {
    lis, _ := net.Listen("tcp", ":50051")
    grpcServer := grpc.NewServer()
    
    // Register your services
    // pb.RegisterYourServiceServer(grpcServer, &yourServiceImpl{})
    
    // Register health check service
    healthServer := health.NewServer()
    grpc_health_v1.RegisterHealthServer(grpcServer, healthServer)
    
    // Set health status
    healthServer.SetServingStatus("", grpc_health_v1.HealthCheckResponse_SERVING)
    healthServer.SetServingStatus("myapp.UserService", grpc_health_v1.HealthCheckResponse_SERVING)
    
    grpcServer.Serve(lis)
}
```

#### Node.js Server

```javascript
const grpc = require('@grpc/grpc-js');
const healthCheck = require('grpc-health-check');

const server = new grpc.Server();

// Add your services
// server.addService(YourService, yourImplementation);

// Add health check service
const healthImpl = new healthCheck.Implementation({
  '': healthCheck.servingStatus.SERVING,
  'myapp.UserService': healthCheck.servingStatus.SERVING,
});
server.addService(healthCheck.service, healthImpl);

server.bindAsync('0.0.0.0:50051', 
  grpc.ServerCredentials.createInsecure(),
  () => {
    server.start();
    console.log('Server running on port 50051');
  }
);
```

#### Java Server

```java
import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.protobuf.services.ProtoReflectionService;
import io.grpc.services.HealthStatusManager;

public class GrpcServer {
    public static void main(String[] args) throws Exception {
        HealthStatusManager healthManager = new HealthStatusManager();
        
        Server server = ServerBuilder.forPort(50051)
            // Add your services
            // .addService(new YourServiceImpl())
            
            // Add health check service
            .addService(healthManager.getHealthService())
            .build()
            .start();
        
        // Set health status
        healthManager.setStatus("", HealthCheckResponse.ServingStatus.SERVING);
        healthManager.setStatus("myapp.UserService", HealthCheckResponse.ServingStatus.SERVING);
        
        server.awaitTermination();
    }
}
```

## Testing the Tool

An example server is included for testing:

```bash
# Terminal 1: Start the example server
uvx --with grpcio --with grpcio-health-checking example_server.py

# Terminal 2: Test health checks
uvx --from . grpc-healthcheck --target localhost:50051 -v
uvx --from . grpc-healthcheck --target localhost:50051 --service example.Service -v
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

