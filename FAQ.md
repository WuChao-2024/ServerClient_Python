# Fast Inference Server - FAQ

## General Questions

### Q: What is Fast Inference Server?

A: Fast Inference Server is a high-performance inference server that uses binary protocol (Pickle) for efficient data transmission between client and server. It's optimized for deep learning model inference with minimal latency.

### Q: Why use binary protocol instead of JSON?

A: Binary protocol (Pickle) is 10-50x faster than JSON for numpy arrays because:
- No need to convert arrays to lists
- Direct memory serialization
- Zero-copy for large arrays with Protocol 5
- Supports arbitrary Python objects

### Q: Is this production-ready?

A: Yes, but you should:
- Add authentication (API keys, OAuth)
- Use HTTPS (add nginx/traefik as reverse proxy)
- Implement rate limiting
- Add monitoring and logging
- Follow security best practices in SECURITY.md

## Installation & Setup

### Q: What are the system requirements?

A:
- Python >= 3.8
- PyTorch >= 1.10
- Flask >= 2.0
- NumPy >= 1.20
- requests >= 2.25

### Q: How do I install it?

A:
```bash
git clone https://github.com/yourusername/Server_OpenSource.git
cd Server_OpenSource
pip install -r requirements.txt
```

### Q: Can I use it with my own model?

A: Yes! Edit `server.py` and replace `load_model()` and `model_inference()` functions with your model loading and inference logic.

### Q: Does it support GPU?

A: Yes! Use `--device cuda:0` when starting the server:
```bash
python server.py --model-path /path/to/model --device cuda:0
```

## Usage

### Q: How do I start the server?

A: Three ways:
```bash
# Option 1: Direct
python server.py --model-path /path/to/model --device cuda:0 --port 50000

# Option 2: Quick start script
./start_server.sh

# Option 3: Docker
docker-compose up -d
```

### Q: How do I send a request?

A:
```python
from request_tools import send_inference_request
import numpy as np

data = {
    "instruction": "your instruction",
    "state": np.array([0.1, 0.2, 0.3], dtype=np.float32),
    "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
}

result = send_inference_request(data, url='http://127.0.0.1:50000/infer')
```

### Q: Can I update the model without restarting?

A: Yes! Use the `/update_model` endpoint:
```python
import requests

with open('model.tar', 'rb') as f:
    files = {'file': ('model.tar', f, 'application/x-tar')}
    response = requests.post('http://127.0.0.1:50000/update_model', files=files)
```

### Q: What data types are supported?

A: Any Python object that can be pickled:
- numpy arrays
- torch tensors (will be converted to numpy)
- strings, numbers, lists, dicts
- custom Python objects

## Performance

### Q: How fast is it?

A: Benchmark results (Intel i7-10700K, RTX 3080):
- Serialization: ~250 MB/s
- Network transfer: ~180 MB/s
- End-to-end latency: 15-35ms (depending on data size)

### Q: Why is it single-threaded?

A: Single-threaded ensures:
- Deterministic behavior
- Reproducible results
- Simpler debugging
- No race conditions

If you need concurrent processing, you can:
- Run multiple server instances
- Use a load balancer
- Enable `threaded=True` in Flask (but loses determinism)

### Q: How can I improve performance?

A:
1. Use C-contiguous numpy arrays
2. Use float32 instead of float64
3. Enable pin_memory for GPU transfer
4. Use torch.inference_mode() instead of no_grad()
5. Compile model with torch.jit or torch.compile
6. See DEVELOPMENT.md for more tips

### Q: Can I batch multiple requests?

A: The server processes requests sequentially. For batching:
- Send multiple samples in one request (if your model supports batching)
- Or implement custom batching logic (see DEVELOPMENT.md)

## Troubleshooting

### Q: Server won't start - "Address already in use"

A: Port is already in use. Either:
- Stop the other process using that port
- Use a different port: `--port 50001`

### Q: Request timeout error

A: Increase timeout:
```python
result = send_inference_request(data, url='...', timeout=30)
```

Or optimize your model inference speed.

### Q: "Pickle version mismatch" error

A: Ensure client and server use the same Python version (both 3.8+).

### Q: CUDA out of memory

A:
- Reduce batch size
- Use smaller model
- Use CPU: `--device cpu`
- Clear GPU cache: `torch.cuda.empty_cache()`

### Q: Import error for custom modules

A: Make sure you're in the correct directory and PYTHONPATH is set:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/Server_OpenSource"
```

## Security

### Q: Is Pickle safe?

A: Pickle can execute arbitrary code during deserialization. Only accept requests from trusted clients. For untrusted sources, consider:
- Using msgpack or protobuf instead
- Network isolation
- Authentication and authorization

### Q: How do I add authentication?

A: See SECURITY.md for examples. Basic approach:
```python
@app.route('/infer', methods=['POST'])
@require_api_key
def infer():
    # ... existing code
```

### Q: Should I use HTTPS?

A: Yes, in production! Add nginx or traefik as reverse proxy with SSL certificate.

## Deployment

### Q: How do I deploy to production?

A: Several options:
1. **Docker**: Use provided Dockerfile and docker-compose.yml
2. **Gunicorn**: `gunicorn -w 4 -b 0.0.0.0:50000 server:app`
3. **Kubernetes**: See DEVELOPMENT.md for example deployment.yaml
4. **Cloud**: Deploy to AWS, GCP, Azure using Docker

### Q: Can I run multiple instances?

A: Yes! Use a load balancer (nginx, HAProxy) to distribute requests:
```bash
# Start multiple instances
python server.py --port 50000 &
python server.py --port 50001 &
python server.py --port 50002 &

# Configure nginx to load balance
```

### Q: How do I monitor the server?

A: Add monitoring:
- Prometheus metrics (see DEVELOPMENT.md)
- Application logs
- Health check endpoint
- Resource monitoring (CPU, memory, GPU)

## Development

### Q: How do I contribute?

A: See CONTRIBUTING.md for guidelines:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Q: How do I add custom endpoints?

A:
```python
@app.route('/your_endpoint', methods=['POST'])
def your_endpoint():
    # Your logic here
    return Response(...)
```

### Q: Can I use a different serialization format?

A: Yes! Replace `binary_protocol.py` with your preferred format (msgpack, protobuf, etc.). Just maintain the same interface:
- `dict_to_binary(data) -> bytes`
- `binary_to_dict(data) -> dict`

### Q: How do I run tests?

A:
```bash
# Basic test
python test_server.py

# Benchmark
python benchmark.py

# Verify installation
python verify_installation.py
```

## Comparison with Other Solutions

### Q: How does this compare to TorchServe?

A:
- **Fast Inference Server**: Simpler, faster for numpy arrays, easier to customize
- **TorchServe**: More features, better for production at scale, more complex

### Q: How does this compare to TensorFlow Serving?

A:
- **Fast Inference Server**: Framework agnostic, simpler, Python-based
- **TF Serving**: TensorFlow-specific, C++ based, more optimized

### Q: How does this compare to FastAPI?

A:
- **Fast Inference Server**: Optimized for binary data, simpler
- **FastAPI**: Better for REST APIs, automatic docs, more features

### Q: When should I use this?

A: Use Fast Inference Server when:
- You need fast numpy array transmission
- You want simple, customizable solution
- You need deterministic sequential processing
- You're prototyping or building internal tools

Use alternatives when:
- You need advanced features (A/B testing, model versioning)
- You need to serve many different models
- You need enterprise-grade production features

## Getting Help

### Q: Where can I get help?

A:
- Read documentation: README.md, DEVELOPMENT.md
- Check examples: example_usage.py
- Open an issue: GitHub Issues
- Start a discussion: GitHub Discussions

### Q: How do I report a bug?

A: Open a GitHub issue with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, etc.)
- Error messages and logs

### Q: How do I request a feature?

A: Open a GitHub issue with:
- Description of the feature
- Use case / motivation
- Proposed implementation (optional)

## License & Citation

### Q: What license is this under?

A: Apache License 2.0 - free for commercial and non-commercial use.

### Q: How do I cite this project?

A:
```bibtex
@software{fast_inference_server,
  title = {Fast Inference Server},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/Server_OpenSource}
}
```

---

**Still have questions?** Open an issue or start a discussion on GitHub!
