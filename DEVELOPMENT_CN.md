# 高性能推理服务器 - 开发指南

[English](DEVELOPMENT.md) | [中文](DEVELOPMENT_CN.md)

## 目录
- [架构概览](#架构概览)
- [自定义服务器](#自定义服务器)
- [性能调优](#性能调优)
- [测试](#测试)
- [部署](#部署)

## 架构概览

### 组件

```
┌─────────────────────────────────────────────────────────┐
│                    客户端应用                             │
└───────────────────────────┬─────────────────────────────┘
                            │
                            │ HTTP POST (二进制)
                            │
┌───────────────────────────▼─────────────────────────────┐
│                      Flask 服务器                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │  /infer 端点                                       │ │
│  │  1. 反序列化 (Pickle)                             │ │
│  │  2. Numpy → Torch                                 │ │
│  │  3. 模型推理                                       │ │
│  │  4. 序列化结果                                     │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │  /update_model 端点                               │ │
│  │  - 热更新模型，无需重启                            │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 数据流

1. **客户端**:
   - 准备数据（包含 numpy 数组的字典）
   - 使用 `dict_to_binary()` 序列化（Pickle Protocol 5）
   - 发送 HTTP POST 请求

2. **服务器端**:
   - 接收二进制数据
   - 使用 `binary_to_dict()` 反序列化
   - 转换 numpy → torch 张量
   - 运行模型推理
   - 序列化结果
   - 返回二进制响应

3. **客户端**:
   - 接收二进制响应
   - 反序列化结果

## 自定义服务器

### 1. 集成自己的模型

编辑 `server.py`：

```python
def load_model(model_path: str, device: torch.device):
    """替换为你的模型加载逻辑"""
    from your_model_package import YourModel

    model = YourModel.from_pretrained(model_path)
    model = model.to(device).eval()

    # 可选：使用 torch.jit 编译以加速推理
    # model = torch.jit.script(model)

    return model


def model_inference(obs: dict) -> np.ndarray:
    """替换为你的推理逻辑"""
    global model, device

    # 你的预处理
    inputs = preprocess(obs)

    # 推理
    with torch.inference_mode():
        output = model(inputs)

    # 你的后处理
    result = postprocess(output)

    return result.detach().cpu().numpy()
```

### 2. 添加自定义端点

```python
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return {"status": "healthy", "model_loaded": model is not None}


@app.route('/model_info', methods=['GET'])
def model_info():
    """获取模型信息"""
    global model
    if model is None:
        return {"error": "Model not loaded"}, 503

    return {
        "model_type": type(model).__name__,
        "device": str(device),
        "parameters": sum(p.numel() for p in model.parameters())
    }
```

### 3. 添加身份验证

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
    # ... 现有代码
```

## 性能调优

### 1. 优化数据传输

**使用 C-contiguous 数组：**
```python
# 客户端
if not array.flags['C_CONTIGUOUS']:
    array = np.ascontiguousarray(array)
```

**使用合适的数据类型：**
```python
# 尽可能使用 float32 而不是 float64
image = image.astype(np.float32)
```

### 2. 优化 GPU 传输

**使用固定内存：**
```python
# 服务器端
tensor = torch.from_numpy(array).pin_memory().to(device, non_blocking=True)
```

**使用 CUDA 流：**
```python
# 在 main() 中
if device.type == 'cuda':
    global inference_stream
    inference_stream = torch.cuda.Stream()

# 在 infer() 中
if device.type == 'cuda':
    with torch.cuda.stream(inference_stream):
        output = model(inputs)
```

### 3. 模型优化

**使用 torch.compile (PyTorch 2.0+)：**
```python
model = torch.compile(model, mode='reduce-overhead')
```

**使用混合精度：**
```python
with torch.cuda.amp.autocast():
    output = model(inputs)
```

**量化：**
```python
model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)
```

### 4. 批处理

如果需要高效处理多个请求：

```python
from queue import Queue
from threading import Thread

request_queue = Queue(maxsize=32)
result_dict = {}

def batch_inference_worker():
    while True:
        batch = []
        batch_ids = []

        # 收集请求
        for _ in range(BATCH_SIZE):
            if not request_queue.empty():
                req_id, data = request_queue.get()
                batch.append(data)
                batch_ids.append(req_id)

        if batch:
            # 批量推理
            results = model_batch_inference(batch)
            for req_id, result in zip(batch_ids, results):
                result_dict[req_id] = result
```

## 测试

### 单元测试

创建 `tests/test_binary_protocol.py`：

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

### 集成测试

创建 `tests/test_server.py`：

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

### 负载测试

```bash
# 安装 locust
pip install locust

# 创建 locustfile.py
# 运行负载测试
locust -f locustfile.py --host http://127.0.0.1:50000
```

## 部署

### 生产服务器 (Gunicorn)

```bash
# 安装
pip install gunicorn

# 使用 4 个 worker 运行
gunicorn -w 4 -b 0.0.0.0:50000 --timeout 120 server:app

# 带日志
gunicorn -w 4 -b 0.0.0.0:50000 --timeout 120 \
    --access-logfile access.log \
    --error-logfile error.log \
    server:app
```

### Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用
COPY . .

# 暴露端口
EXPOSE 50000

# 运行服务器
CMD ["python", "server.py", "--model-path", "/models", "--device", "cpu", "--port", "50000", "--host", "0.0.0.0"]
```

构建和运行：

```bash
docker build -t inference-server .
docker run -p 50000:50000 -v /path/to/models:/models inference-server
```

### Kubernetes 部署

创建 `deployment.yaml`：

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

### 监控

添加 Prometheus 指标：

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('inference_requests_total', '总推理请求数')
REQUEST_LATENCY = Histogram('inference_latency_seconds', '推理延迟')

@app.route('/metrics')
def metrics():
    return generate_latest()

@app.route('/infer', methods=['POST'])
def infer():
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        # ... 现有推理代码
```

## 故障排除

### 常见问题

1. **Pickle 版本不匹配**：确保客户端和服务器使用相同的 Python 版本
2. **内存问题**：减少批量大小或使用更小的数据类型
3. **超时错误**：增加超时时间或优化模型推理
4. **CUDA 内存不足**：减小模型大小或使用 CPU

### 调试模式

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 性能分析

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# 你的代码

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

## 贡献

参见 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献指南。

## 许可证

Apache License 2.0
