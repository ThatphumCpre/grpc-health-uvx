# gRPC Health Check Tool

เครื่องมือตรวจสอบสุขภาพของ gRPC server แบบง่ายๆ ที่ใช้ standard gRPC Health Checking Protocol (grpc.health.v1)

## การติดตั้ง

### ใช้งานผ่าน uvx (แนะนำ)

ไม่ต้องติดตั้ง สามารถรันได้เลย:

```bash
# รันจากโฟลเดอร์นี้
uvx --from . grpc-healthcheck --target localhost:50051

# หรือ clone แล้วรัน
uvx --from git+https://github.com/yourusername/grpcheck grpc-healthcheck --target localhost:50051
```

### ติดตั้งด้วย pip/uv

```bash
# ใช้ uv
uv pip install -e .

# หรือใช้ pip
pip install -e .
```

## การใช้งาน

### Basic Usage

```bash
# ตรวจสอบสุขภาพโดยรวมของ server
uvx --from . grpc-healthcheck --target localhost:50051

# ตรวจสอบ service เฉพาะ
uvx --from . grpc-healthcheck --target localhost:50051 --service myapp.UserService

# ใช้ host และ port แยก
uvx --from . grpc-healthcheck --host localhost --port 50051
```

### Advanced Options

```bash
# เปิด verbose mode เพื่อดูรายละเอียด
uvx --from . grpc-healthcheck --target localhost:50051 -v

# ใช้ TLS/SSL
uvx --from . grpc-healthcheck --target secure.example.com:443 --tls

# กำหนด timeout (default: 5 วินาที)
uvx --from . grpc-healthcheck --target localhost:50051 --timeout 10

# รวมทุกอย่าง
uvx --from . grpc-healthcheck \
  --target secure.example.com:443 \
  --service myapp.UserService \
  --tls \
  --timeout 10 \
  -v
```

## Exit Codes

- `0`: Service มีสุขภาพดี (SERVING)
- `1`: Service ไม่พร้อม (NOT_SERVING, UNKNOWN, หรือมี error)

## ตัวอย่างการใช้งานใน Scripts

### Shell Script

```bash
#!/bin/bash

if uvx --from . grpc-healthcheck --target localhost:50051; then
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

# Copy health check tool
COPY grpc_healthcheck.py pyproject.toml /app/
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD uvx --from . grpc-healthcheck --target localhost:50051 || exit 1

CMD ["your-grpc-server"]
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
    livenessProbe:
      exec:
        command:
        - uvx
        - --from
        - /app/healthcheck
        - grpc-healthcheck
        - --target
        - localhost:50051
      initialDelaySeconds: 5
      periodSeconds: 10
    readinessProbe:
      exec:
        command:
        - uvx
        - --from
        - /app/healthcheck
        - grpc-healthcheck
        - --target
        - localhost:50051
        - --service
        - myapp.UserService
      initialDelaySeconds: 3
      periodSeconds: 5
```

### CI/CD Integration

```yaml
# GitHub Actions
- name: Wait for gRPC server
  run: |
    for i in {1..30}; do
      if uvx --from . grpc-healthcheck --target localhost:50051; then
        echo "Server is ready!"
        exit 0
      fi
      echo "Waiting for server... ($i/30)"
      sleep 2
    done
    echo "Server failed to start"
    exit 1
```

## Requirements

- Python 3.8+
- grpcio
- grpcio-health-checking

## gRPC Health Checking Protocol

เครื่องมือนี้ใช้ [gRPC Health Checking Protocol](https://github.com/grpc/grpc/blob/master/doc/health-checking.md) ซึ่งเป็น standard ของ gRPC

Server ของคุณต้อง implement `grpc.health.v1.Health` service เพื่อให้ health check ทำงานได้

### การเพิ่ม Health Check ใน gRPC Server

#### Python Server

```python
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

# สร้าง health servicer
health_servicer = health.HealthServicer()
health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
health_servicer.set("myapp.UserService", health_pb2.HealthCheckResponse.SERVING)

# เพิ่มใน server
health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
```

#### Go Server

```go
import "google.golang.org/grpc/health/grpc_health_v1"

// Register health server
healthServer := health.NewServer()
grpc_health_v1.RegisterHealthServer(grpcServer, healthServer)
healthServer.SetServingStatus("", grpc_health_v1.HealthCheckResponse_SERVING)
```

## License

MIT

