# Fast Inference Server - Getting Started Guide

Welcome! This guide will help you get started with Fast Inference Server in 5 minutes.

## 📋 Prerequisites

Before you begin, make sure you have:
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)

## 🚀 Step-by-Step Setup

### Step 1: Get the Code

**Option A: Clone from GitHub**
```bash
git clone https://github.com/yourusername/Server_OpenSource.git
cd Server_OpenSource
```

**Option B: Download ZIP**
- Download and extract the ZIP file
- Navigate to the extracted directory

### Step 2: Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python verify_installation.py
```

You should see:
```
✓ All checks passed! Installation is successful.
```

### Step 4: Prepare Your Model

You have two options:

**Option A: Use Dummy Model (for testing)**
```bash
# The server includes a dummy model for testing
# No additional setup needed
```

**Option B: Use Your Own Model**
1. Prepare your model directory with required files
2. Edit `server.py` to customize `load_model()` and `model_inference()`

### Step 5: Start the Server

```bash
python server.py --model-path ./dummy_model --device cpu --port 50000
```

You should see:
```
[InferenceServer] [20:00:00.000] [INFO] Loading model...
[InferenceServer] [20:00:01.000] [INFO] Model loaded successfully!
[InferenceServer] [20:00:01.000] [INFO] Server starting on 127.0.0.1:50000
```

### Step 6: Test the Server

Open a new terminal and run:

```bash
python test_server.py
```

You should see:
```
✓ All tests passed!
```

## 🎉 Congratulations!

You've successfully set up Fast Inference Server! Here's what you can do next:

### Try the Examples

```bash
python example_usage.py
```

### Run Benchmarks

```bash
python benchmark.py
```

### Profile Performance

```bash
python profiler.py
```

## 📝 Your First Request

Create a file `my_first_request.py`:

```python
from request_tools import send_inference_request
import numpy as np

# Prepare your data
data = {
    "instruction": "Hello, server!",
    "state": np.array([1.0, 2.0, 3.0], dtype=np.float32),
    "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
}

# Send request
result = send_inference_request(
    data_dict=data,
    url='http://127.0.0.1:50000/infer',
    timeout=10
)

# Print result
print(f"Status: {result['status']}")
print(f"Output: {result['output']}")
```

Run it:
```bash
python my_first_request.py
```

## 🔧 Customizing for Your Model

### 1. Edit server.py

Find the `load_model()` function:

```python
def load_model(model_path: str, device: torch.device):
    """Replace with your model loading logic"""
    # Example:
    from your_package import YourModel
    model = YourModel.from_pretrained(model_path)
    return model.to(device).eval()
```

Find the `model_inference()` function:

```python
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

### 2. Restart the Server

```bash
python server.py --model-path /path/to/your/model --device cuda:0 --port 50000
```

### 3. Test Your Changes

```bash
python test_server.py
```

## 🐳 Using Docker (Optional)

### Build Docker Image

```bash
docker build -t inference-server .
```

### Run Container

```bash
docker run -p 50000:50000 -v /path/to/models:/models inference-server
```

### Or Use Docker Compose

```bash
docker-compose up -d
```

## 📚 Next Steps

### Learn More
- Read [README.md](README.md) for detailed documentation
- Check [DEVELOPMENT.md](DEVELOPMENT.md) for advanced customization
- Browse [FAQ.md](FAQ.md) for common questions

### Optimize Performance
- Read performance tips in [DEVELOPMENT.md](DEVELOPMENT.md)
- Run [profiler.py](profiler.py) to identify bottlenecks
- Check [benchmark.py](benchmark.py) results

### Deploy to Production
- Add authentication (see [SECURITY.md](SECURITY.md))
- Use HTTPS with reverse proxy
- Set up monitoring and logging
- Follow deployment guide in [DEVELOPMENT.md](DEVELOPMENT.md)

## ❓ Troubleshooting

### Server won't start

**Problem:** Port already in use
```
OSError: [Errno 48] Address already in use
```

**Solution:** Use a different port
```bash
python server.py --model-path ./dummy_model --device cpu --port 50001
```

### Import errors

**Problem:** Module not found
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### CUDA errors

**Problem:** CUDA out of memory
```
RuntimeError: CUDA out of memory
```

**Solution:** Use CPU or smaller model
```bash
python server.py --model-path ./dummy_model --device cpu --port 50000
```

### Request timeout

**Problem:** Request takes too long
```
RuntimeError: Request timeout
```

**Solution:** Increase timeout
```python
result = send_inference_request(data, url='...', timeout=30)
```

## 💡 Tips

### Tip 1: Use Virtual Environment
Always use a virtual environment to avoid dependency conflicts:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Tip 2: Check Logs
Server logs show detailed information about requests:
```
[InferenceServer] [20:00:00.000] [INFO] Deserialize time = 2.50 ms
[InferenceServer] [20:00:00.010] [INFO] cuda:0 inference time = 15.30 ms
[InferenceServer] [20:00:00.020] [INFO] Serialize time = 1.80 ms
```

### Tip 3: Use Quick Start Script
For automated setup:
```bash
./setup_and_test.sh
```

### Tip 4: Test Before Deploying
Always test your changes:
```bash
python test_server.py
python benchmark.py
```

### Tip 5: Read the Documentation
The documentation is comprehensive:
- [README.md](README.md) - Overview
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide
- [FAQ.md](FAQ.md) - Common questions
- [SECURITY.md](SECURITY.md) - Security practices

## 🎯 Quick Reference

### Start Server
```bash
python server.py --model-path /path/to/model --device cuda:0 --port 50000
```

### Test Server
```bash
python test_server.py
```

### Send Request
```python
from request_tools import send_inference_request
result = send_inference_request(data, url='http://127.0.0.1:50000/infer')
```

### Update Model
```python
import requests
with open('model.tar', 'rb') as f:
    files = {'file': ('model.tar', f, 'application/x-tar')}
    requests.post('http://127.0.0.1:50000/update_model', files=files)
```

## 📞 Get Help

- **Documentation:** Check [README.md](README.md) and [FAQ.md](FAQ.md)
- **Issues:** Report bugs on GitHub Issues
- **Discussions:** Ask questions on GitHub Discussions
- **Email:** security@yourproject.com (for security issues)

## ✅ Checklist

Before moving to production:

- [ ] Tested with your model
- [ ] Added authentication
- [ ] Configured HTTPS
- [ ] Set up monitoring
- [ ] Reviewed security practices
- [ ] Tested error handling
- [ ] Documented your customizations
- [ ] Set up backups

## 🎊 You're Ready!

You now have a working Fast Inference Server! Start building amazing applications!

---

**Need help?** Check [FAQ.md](FAQ.md) or open an issue on GitHub.

**Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md).

**Happy coding! 🚀**
