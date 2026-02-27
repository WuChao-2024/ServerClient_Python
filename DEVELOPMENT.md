# Fast Inference Server - Development Guide

[English](DEVELOPMENT.md) | [中文](DEVELOPMENT_CN.md)

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Customizing the Server](#customizing-the-server)
- [Performance Tuning](#performance-tuning)
- [Testing](#testing)
- [Deployment](#deployment)

## Architecture Overview

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    Client Application                    │
└───────────────────────────┬─────────────────────────────┘
                            │
                            │ HTTP POST (Binary)
                            │
┌───────────────────────────▼─────────────────────────────┐
│                      Flask Server                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │  /infer endpoint                                   │ │
│  │  1. Deserialize (Pickle)                          │ │
│  │  2. Numpy → Torch                                 │ │
│  │  3. Model Inference                               │ │
│  │  4. Serialize Result                              │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │  /update_model endpoint                           │ │
│  │  - Hot reload model without restart               │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Client Side**:
   - Prepare data (dict with numpy arrays)
   - Serialize with `dict_to_binary()` (Pickle Protocol 5)
   - Send HTTP POST request

2. **Server Side**:
   - Receive binary data
   - Deserialize with `binary_to_dict()`
   - Convert numpy → torch tensors
   - Run model inference
   - Serialize result
   - Return binary response

3. **Client Side**:
   - Receive binary response
   - Deserialize result

## Customizing the Server

### 1. Integrate Your Own Model

Edit `server.py`:

```python
def load_model(model_path: str, device: torch.device):
    """Replace with your model loading logic"""
    from your_model_package import YourModel

    model = YourModel.from_pretrained(model_path)
    model = model.to(device).eval()

    # Optional: Compile with torch.jit for faster inference
    # model = torch.jit.script(model)

    return model


def model_inference(obs: dict) -> np.ndarray:
    """Replace with your inference logic"""
    global model, device

    # Your preprocessing
    inputs = preprocess(obs)

    # Inference
    with torch.inference_mode():
        output = model(inputs)

    # Your postprocessing
    result = postprocess(output)

    return result.detach().cpu().numpy()
```

### 2. Add Custom Endpoints

```python
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": model is not None}


@app.route('/model_info', methods=['GET'])
def model_info():
    """Get model information"""
    global model
    if model is None:
        return {"error": "Model not loaded"}, 503

    return {
        "model_type": type(model).__name__,
        "device": str(device),
        "parameters": sum(p.numel() for p in model.parameters())
    }
```

### 3. Add Authentication

```python
from functools import wraps
from flask import request

API_KEY = "your-secret-key"

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return {"error": "Invalid API key"}, 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/infer', methods=['POST'])
@require_api_key
def infer():
    # ... existing code
```

## Performance Tuning

### 1. Optimize Data Transfer

**Use C-contiguous arrays:**
```python
# Client side
if not array.flags['C_CONTIGUOUS']:
    array = np.ascontiguousarray(array)
```

**Use appropriate dtypes:**
```python
# Use float32 instead of float64 when possible
image = image.astype(np.float32)
```

### 2. Optimize GPU Transfer

**Use pinned memory:**
```python
# Server side
tensor = torch.from_numpy(array).pin_memory().to(device, non_blocking=True)
```

**Use CUDA streams:**
```python
# In main()
if device.type == 'cuda':
    global inference_stream
    inference_stream = torch.cuda.Stream()

# In infer()
if device.type == 'cuda':
    with torch.cuda.stream(inference_stream):
        output = model(inputs)
```

### 3. Model Optimization

**Use torch.compile (PyTorch 2.0+):**
```python
model = torch.compile(model, mode='reduce-overhead')
```

**Use mixed precision:**
```python
with torch.cuda.amp.autocast():
    output = model(inputs)
```

**Quantization:**
```python
model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)
```

### 4. Batch Processing

If you need to handle multiple requests efficiently:

```python
from queue import Queue
from threading import Thread

request_queue = Queue(maxsize=32)
result_dict = {}

def batch_inference_worker():
    while True:
        batch = []
        batch_ids = []

        # Collect requests
        for _ in range(BATCH_SIZE):
            if not request_queue.empty():
                req_id, data = request_queue.get()
                batch.append(data)
                batch_ids.append(req_id)

        if batch:
            # Batch inference
            results = model_batch_inference(batch)
            for req_id, result in zip(batch_ids, results):
                result_dict[req_id] = result
```

## Testing

### Unit Tests

Create `tests/test_binary_protocol.py`:

```python
import unittest
import numpy as np
from binary_protocol import dict_to_binary, binary_to_dict


class TestBinaryProtocol(unittest.TestCase):
    def test_simple_dict(self):
        data = {"key": "value", "number": 42}
        binary = dict_to_binary(data)
        restored = binary_to_dict(binary)
        self.assertEqual(data, restored)

    def test_numpy_array(self):
        data = {"array": np.random.randn(100, 100).astype(np.float32)}
        binary = dict_to_binary(data)
        restored = binary_to_dict(binary)
        np.testing.assert_array_equal(data["array"], restored["array"])


if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

Create `tests/test_server.py`:

```python
import unittest
import numpy as np
from request_tools import send_inference_request


class TestServer(unittest.TestCase):
    SERVER_URL = 'http://127.0.0.1:50000/infer'

    def test_inference(self):
        data = {
            "state": np.random.randn(6).astype(np.float32),
            "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        }
        result = send_inference_request(data, url=self.SERVER_URL)
        self.assertIn("status", result)
        self.assertEqual(result["status"], "ok")


if __name__ == '__main__':
    unittest.main()
```

### Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
# Run load test
locust -f locustfile.py --host http://127.0.0.1:50000
```

## Deployment

### Production Server (Gunicorn)

```bash
# Install
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:50000 --timeout 120 server:app

# With logging
gunicorn -w 4 -b 0.0.0.0:50000 --timeout 120 \
    --access-logfile access.log \
    --error-logfile error.log \
    server:app
```

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 50000

# Run server
CMD ["python", "server.py", "--model-path", "/models", "--device", "cpu", "--port", "50000", "--host", "0.0.0.0"]
```

Build and run:

```bash
docker build -t inference-server .
docker run -p 50000:50000 -v /path/to/models:/models inference-server
```

### Kubernetes Deployment

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inference-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: inference-server
  template:
    metadata:
      labels:
        app: inference-server
    spec:
      containers:
      - name: server
        image: inference-server:latest
        ports:
        - containerPort: 50000
        resources:
          limits:
            nvidia.com/gpu: 1
        volumeMounts:
        - name: model-storage
          mountPath: /models
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-pvc
```

### Monitoring

Add Prometheus metrics:

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('inference_requests_total', 'Total inference requests')
REQUEST_LATENCY = Histogram('inference_latency_seconds', 'Inference latency')

@app.route('/metrics')
def metrics():
    return generate_latest()

@app.route('/infer', methods=['POST'])
def infer():
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        # ... existing inference code
```

## Troubleshooting

### Common Issues

1. **Pickle version mismatch**: Ensure both client and server use same Python version
2. **Memory issues**: Reduce batch size or use smaller data types
3. **Timeout errors**: Increase timeout or optimize model inference
4. **CUDA out of memory**: Reduce model size or use CPU

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Apache License 2.0
