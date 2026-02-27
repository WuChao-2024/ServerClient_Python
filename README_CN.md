# 高性能推理服务器

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[English](README.md) | [中文](README_CN.md)

一个使用二进制协议（Pickle）实现的高性能推理服务器，用于客户端和服务器之间的快速数据传输。针对深度学习模型推理进行了优化，延迟最小化。


## ✨ 特性

- **二进制协议**：使用 Pickle Protocol 5 高效序列化 Python 对象和 numpy 数组
- **零拷贝优化**：最小化传输过程中的数据拷贝开销
- **简单 API**：基于 Flask 的易用 REST API
- **灵活性强**：支持任意 Python 对象序列化，不限于特定数据类型
- **热更新模型**：支持动态更新模型，无需重启服务器
- **健壮的客户端**：自动重试逻辑，可配置超时
- **单线程**：确定性的顺序处理，保证结果可复现

## 🏗️ 架构

```
客户端                          服务器
  |                               |
  |  1. 序列化数据 (Pickle)        |
  |------------------------------>|
  |                               | 2. 反序列化
  |                               | 3. 模型推理
  |                               | 4. 序列化结果
  |<------------------------------|
  |  5. 反序列化结果               |
```

**为什么使用二进制协议？**
- 对于 numpy 数组，比 JSON 快 10-50 倍
- 支持任意 Python 对象
- Protocol 5 对大型数组实现零拷贝
- CPU 开销最小

## 📦 安装

### 依赖要求

- Python >= 3.8
- PyTorch >= 1.10
- Flask >= 2.0
- NumPy >= 1.20
- requests >= 2.25

### 从源码安装

```bash
git clone https://github.com/yourusername/Server_OpenSource.git
cd Server_OpenSource
pip install -r requirements.txt
```

## 🚀 快速开始

### 1. 启动服务器

**方式 A：使用快速启动脚本**

```bash
./start_server.sh
```

**方式 B：手动启动**

```bash
python server.py --model-path /path/to/your/model --device cuda:0 --port 50000
```

参数说明：
- `--model-path`：模型目录路径（必需）
- `--device`：推理设备（默认：`cpu`）
- `--port`：服务器端口（默认：`50000`）
- `--host`：服务器主机（默认：`127.0.0.1`）

### 2. 发送推理请求

```python
from request_tools import send_inference_request
import numpy as np

# 准备数据
data = {
    "instruction": "你的指令",
    "state": np.array([0.1, 0.2, 0.3], dtype=np.float32),
    "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
}

# 发送请求
result = send_inference_request(
    data_dict=data,
    url='http://127.0.0.1:50000/infer',
    timeout=10
)

print(result)
```

### 3. 测试服务器

```bash
# 运行基础测试
python test_server.py

# 运行综合性能测试
python benchmark.py
```

## 📚 使用示例

### 基础推理

```python
from request_tools import send_inference_request
import numpy as np

data = {
    "instruction": "拿起红色杯子",
    "state": np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6], dtype=np.float32),
    "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
}

result = send_inference_request(data, url='http://127.0.0.1:50000/infer')
print(f"状态: {result['status']}")
print(f"输出: {result['output']}")
```

### 批量处理

```python
import numpy as np
from request_tools import send_inference_request

# 顺序处理多个样本
for i in range(10):
    data = {
        "instruction": f"任务 {i}",
        "state": np.random.randn(6).astype(np.float32),
        "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    }
    result = send_inference_request(data, url='http://127.0.0.1:50000/infer')
    print(f"任务 {i}: {result['status']}")
```

### 错误处理

```python
from request_tools import send_inference_request

try:
    result = send_inference_request(
        data_dict=data,
        url='http://127.0.0.1:50000/infer',
        timeout=10,
        max_retries=3,
        retry_delay=1.0
    )
except RuntimeError as e:
    print(f"请求失败: {e}")
```

### 更多示例

查看 [example_usage.py](example_usage.py) 获取更多综合示例。

## 📖 API 参考

### POST /infer

推理接口。

**请求：**
- Content-Type: `application/octet-stream`
- Body: Pickle 序列化的二进制数据

**响应：**
- Content-Type: `application/octet-stream`
- Body: 包含推理结果的二进制数据

**响应示例：**
```python
{
    "status": "ok",
    "output": numpy.ndarray  # 模型输出
}
```

**错误响应：**
```python
{
    "status": "error",
    "message": "错误描述"
}
```

### POST /update_model

动态更新模型，无需重启服务器。

**请求：**
- Content-Type: `multipart/form-data`
- File: 包含模型文件的 `.tar` 压缩包
- Form data: `device`（可选，如 "cuda:0"、"cpu"）

**响应：**
```json
{
    "message": "Policy updated successfully"
}
```

**示例：**
```python
import requests

with open('model.tar', 'rb') as f:
    files = {'file': ('model.tar', f, 'application/x-tar')}
    data = {'device': 'cuda:0'}
    response = requests.post('http://127.0.0.1:50000/update_model',
                            files=files, data=data)
print(response.json())
```

## ⚡ 性能

### 基准测试结果

测试环境：Intel i7-10700K, 32GB RAM, RTX 3080

| 数据大小 | 序列化 | 反序列化 | 端到端延迟 |
|---------|--------|---------|-----------|
| 小 (VGA) | 2.5 ms | 1.8 ms | 15 ms |
| 中 (HD) | 5.2 ms | 3.6 ms | 22 ms |
| 大 (Full HD) | 12.8 ms | 8.4 ms | 35 ms |

**吞吐量：** 序列化约 250 MB/s，网络传输约 180 MB/s

### 性能优化建议

1. **使用 C-contiguous 数组**：确保 numpy 数组是 C-contiguous 的
2. **使用合适的数据类型**：尽可能使用 `float32` 而不是 `float64`
3. **批处理**：如果模型支持，在一个请求中发送多个样本
4. **固定内存**：启用固定内存以加速 CPU-GPU 传输（参见 [DEVELOPMENT_CN.md](DEVELOPMENT_CN.md)）

运行你自己的基准测试：
```bash
python benchmark.py
```

## 🛠️ 开发

### 项目结构

```
Server_OpenSource/
├── README.md              # 英文文档
├── README_CN.md           # 中文文档
├── requirements.txt       # Python 依赖
├── server.py             # 服务器主实现
├── request_tools.py      # 客户端请求工具
├── binary_protocol.py    # 序列化/反序列化
├── tools.py              # 辅助函数
├── example_usage.py      # 使用示例
├── test_server.py        # 服务器测试
├── benchmark.py          # 性能基准测试
├── start_server.sh       # 快速启动脚本
├── DEVELOPMENT.md        # 开发指南
├── DEVELOPMENT_CN.md     # 开发指南（中文）
├── CONTRIBUTING.md       # 贡献指南
├── CHANGELOG.md          # 版本历史
└── LICENSE               # Apache 2.0 许可证
```

### 自定义

查看 [DEVELOPMENT_CN.md](DEVELOPMENT_CN.md) 获取详细说明：
- 集成自己的模型
- 添加自定义端点
- 性能优化
- 测试和部署

### 运行测试

```bash
# 基础功能测试
python test_server.py

# 性能基准测试
python benchmark.py

# 运行示例
python example_usage.py
```

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献指南。

### 贡献方向

- 添加更全面的测试
- 改进错误处理
- 添加性能基准测试
- 改进文档
- 添加 gRPC 协议支持
- 实现请求批处理
- 添加模型版本管理

## 📄 许可证

本项目采用 Apache License 2.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 📮 联系方式

- 问题反馈：[GitHub Issues](https://github.com/yourusername/Server_OpenSource/issues)
- 讨论：[GitHub Discussions](https://github.com/yourusername/Server_OpenSource/discussions)

## 🙏 致谢

- 基于 [Flask](https://flask.palletsprojects.com/) 构建
- 由 [PyTorch](https://pytorch.org/) 驱动
- 使用 Python [Pickle](https://docs.python.org/3/library/pickle.html) 序列化

## 📊 引用

如果您在研究中使用了本项目，请引用：

```bibtex
@software{fast_inference_server,
  title = {Fast Inference Server: High-Performance Binary Protocol for Deep Learning Inference},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/Server_OpenSource}
}
```

---

**如果觉得有帮助，请给个 Star ⭐！**
