# Fast Inference Server - Project Summary

## 📦 What is this project?

Fast Inference Server is a high-performance inference server designed for deep learning models. It uses binary protocol (Pickle) for efficient data transmission between client and server, achieving 10-50x faster serialization compared to JSON for numpy arrays.

## 🎯 Key Features

1. **Binary Protocol**: Pickle Protocol 5 for efficient serialization
2. **Single-threaded**: Deterministic sequential processing
3. **Hot Model Update**: Update models without server restart
4. **Robust Client**: Automatic retry with configurable timeout
5. **Flexible**: Supports any Python object, not just specific types

## 📁 Project Structure

```
Server_OpenSource/
├── Core Files
│   ├── server.py              # Main server implementation
│   ├── request_tools.py       # Client utilities
│   ├── binary_protocol.py     # Serialization logic
│   └── tools.py               # Helper functions
│
├── Documentation
│   ├── README.md              # English documentation
│   ├── README_CN.md           # Chinese documentation
│   ├── DEVELOPMENT.md         # Development guide (EN)
│   ├── DEVELOPMENT_CN.md      # Development guide (CN)
│   ├── CONTRIBUTING.md        # Contribution guidelines
│   └── CHANGELOG.md           # Version history
│
├── Examples & Tests
│   ├── example_usage.py       # Usage examples
│   ├── test_server.py         # Server tests
│   └── benchmark.py           # Performance benchmarks
│
├── Deployment
│   ├── Dockerfile             # Docker image
│   ├── docker-compose.yml     # Docker Compose config
│   ├── start_server.sh        # Quick start script
│   └── requirements.txt       # Python dependencies
│
└── Configuration
    ├── setup.py               # Package setup
    ├── MANIFEST.in            # Package manifest
    ├── .gitignore             # Git ignore rules
    └── LICENSE                # Apache 2.0 license
```

## 🚀 Quick Start

### Option 1: Direct Run
```bash
python server.py --model-path /path/to/model --device cuda:0 --port 50000
```

### Option 2: Using Script
```bash
./start_server.sh
```

### Option 3: Docker
```bash
docker-compose up -d
```

## 📊 Performance

- **Serialization**: ~250 MB/s
- **Network Transfer**: ~180 MB/s
- **Latency**: 15-35ms (depending on data size)

## 🔧 Customization

### Integrate Your Model

Edit `server.py`:

```python
def load_model(model_path: str, device: torch.device):
    # Replace with your model loading logic
    model = YourModel.from_pretrained(model_path)
    return model.to(device).eval()

def model_inference(obs: dict) -> np.ndarray:
    # Replace with your inference logic
    with torch.inference_mode():
        output = model(obs)
    return output.detach().cpu().numpy()
```

### Add Custom Endpoints

```python
@app.route('/your_endpoint', methods=['POST'])
def your_endpoint():
    # Your custom logic
    return Response(...)
```

## 📝 Usage Example

```python
from request_tools import send_inference_request
import numpy as np

data = {
    "instruction": "pick up the cup",
    "state": np.array([0.1, 0.2, 0.3], dtype=np.float32),
    "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
}

result = send_inference_request(
    data_dict=data,
    url='http://127.0.0.1:50000/infer',
    timeout=10
)

print(result)
```

## 🧪 Testing

```bash
# Basic test
python test_server.py

# Performance benchmark
python benchmark.py

# Run examples
python example_usage.py
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t inference-server .

# Run container
docker run -p 50000:50000 -v /path/to/models:/models inference-server

# Or use docker-compose
docker-compose up -d
```

## 📚 Documentation

- **README.md**: Project overview and quick start
- **DEVELOPMENT.md**: Detailed development guide
- **CONTRIBUTING.md**: How to contribute
- **API Reference**: See README.md for API documentation

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Priority Areas
- [ ] Add comprehensive tests
- [ ] Improve error handling
- [ ] Add gRPC support
- [ ] Implement request batching
- [ ] Add model versioning

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE) file

## 🔗 Links

- GitHub: https://github.com/yourusername/Server_OpenSource
- Issues: https://github.com/yourusername/Server_OpenSource/issues
- Discussions: https://github.com/yourusername/Server_OpenSource/discussions

## 📞 Support

- Open an issue for bugs
- Start a discussion for questions
- Check documentation first

## 🎓 Learn More

1. Read [README.md](README.md) for overview
2. Follow [Quick Start](#quick-start) to get running
3. Check [example_usage.py](example_usage.py) for examples
4. Read [DEVELOPMENT.md](DEVELOPMENT.md) for customization
5. Run [benchmark.py](benchmark.py) to test performance

## ✅ Checklist for Users

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Prepare your model
- [ ] Customize `load_model()` and `model_inference()` in server.py
- [ ] Start server: `python server.py --model-path /path/to/model`
- [ ] Test with: `python test_server.py`
- [ ] Integrate into your application

## 🌟 Why Use This?

1. **Fast**: 10-50x faster than JSON for numpy arrays
2. **Simple**: Easy to integrate and customize
3. **Flexible**: Supports any Python object
4. **Robust**: Automatic retry and error handling
5. **Production-ready**: Docker support, comprehensive docs

---

**Happy Coding! 🚀**
