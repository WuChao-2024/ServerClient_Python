# 快速推理服务器 - 项目总结

## 📦 这是什么项目？

快速推理服务器是一个为深度学习模型设计的高性能推理服务器。它使用二进制协议（Pickle）在客户端和服务器之间进行高效的数据传输，对于 numpy 数组，序列化速度比 JSON 快 10-50 倍。

## 🎯 核心特性

1. **二进制协议**：使用 Pickle Protocol 5 高效序列化
2. **单线程**：确定性的顺序处理
3. **热更新模型**：无需重启服务器即可更新模型
4. **健壮的客户端**：自动重试，可配置超时
5. **灵活性强**：支持任意 Python 对象，不限于特定类型

## 📁 项目结构

```
Server_OpenSource/
├── 核心文件
│   ├── server.py              # 服务器主实现
│   ├── request_tools.py       # 客户端工具
│   ├── binary_protocol.py     # 序列化逻辑
│   └── tools.py               # 辅助函数
│
├── 文档
│   ├── README.md              # 英文文档
│   ├── README_CN.md           # 中文文档
│   ├── DEVELOPMENT.md         # 开发指南（英文）
│   ├── DEVELOPMENT_CN.md      # 开发指南（中文）
│   ├── CONTRIBUTING.md        # 贡献指南
│   └── CHANGELOG.md           # 版本历史
│
├── 示例和测试
│   ├── example_usage.py       # 使用示例
│   ├── test_server.py         # 服务器测试
│   └── benchmark.py           # 性能基准测试
│
├── 部署
│   ├── Dockerfile             # Docker 镜像
│   ├── docker-compose.yml     # Docker Compose 配置
│   ├── start_server.sh        # 快速启动脚本
│   └── requirements.txt       # Python 依赖
│
└── 配置
    ├── setup.py               # 包设置
    ├── MANIFEST.in            # 包清单
    ├── .gitignore             # Git 忽略规则
    └── LICENSE                # Apache 2.0 许可证
```

## 🚀 快速开始

### 方式 1：直接运行
```bash
python server.py --model-path /path/to/model --device cuda:0 --port 50000
```

### 方式 2：使用脚本
```bash
./start_server.sh
```

### 方式 3：Docker
```bash
docker-compose up -d
```

## 📊 性能

- **序列化**：约 250 MB/s
- **网络传输**：约 180 MB/s
- **延迟**：15-35ms（取决于数据大小）

## 🔧 自定义

### 集成你的模型

编辑 `server.py`：

```python
def load_model(model_path: str, device: torch.device):
    # 替换为你的模型加载逻辑
    model = YourModel.from_pretrained(model_path)
    return model.to(device).eval()

def model_inference(obs: dict) -> np.ndarray:
    # 替换为你的推理逻辑
    with torch.inference_mode():
        output = model(obs)
    return output.detach().cpu().numpy()
```

### 添加自定义端点

```python
@app.route('/your_endpoint', methods=['POST'])
def your_endpoint():
    # 你的自定义逻辑
    return Response(...)
```

## 📝 使用示例

```python
from request_tools import send_inference_request
import numpy as np

data = {
    "instruction": "拿起杯子",
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

## 🧪 测试

```bash
# 基础测试
python test_server.py

# 性能基准测试
python benchmark.py

# 运行示例
python example_usage.py
```

## 🐳 Docker 部署

```bash
# 构建镜像
docker build -t inference-server .

# 运行容器
docker run -p 50000:50000 -v /path/to/models:/models inference-server

# 或使用 docker-compose
docker-compose up -d
```

## 📚 文档

- **README_CN.md**：项目概览和快速开始
- **DEVELOPMENT_CN.md**：详细开发指南
- **CONTRIBUTING.md**：如何贡献
- **API 参考**：查看 README_CN.md 中的 API 文档

## 🤝 贡献

欢迎贡献！查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献指南。

### 优先方向
- [ ] 添加全面的测试
- [ ] 改进错误处理
- [ ] 添加 gRPC 支持
- [ ] 实现请求批处理
- [ ] 添加模型版本管理

## 📄 许可证

Apache License 2.0 - 查看 [LICENSE](LICENSE) 文件

## 🔗 链接

- GitHub: https://github.com/yourusername/Server_OpenSource
- 问题反馈: https://github.com/yourusername/Server_OpenSource/issues
- 讨论: https://github.com/yourusername/Server_OpenSource/discussions

## 📞 支持

- 提交 issue 报告 bug
- 发起讨论提问
- 先查看文档

## 🎓 学习更多

1. 阅读 [README_CN.md](README_CN.md) 了解概览
2. 按照[快速开始](#快速开始)运行
3. 查看 [example_usage.py](example_usage.py) 学习示例
4. 阅读 [DEVELOPMENT_CN.md](DEVELOPMENT_CN.md) 了解自定义
5. 运行 [benchmark.py](benchmark.py) 测试性能

## ✅ 用户检查清单

- [ ] 安装依赖：`pip install -r requirements.txt`
- [ ] 准备你的模型
- [ ] 在 server.py 中自定义 `load_model()` 和 `model_inference()`
- [ ] 启动服务器：`python server.py --model-path /path/to/model`
- [ ] 测试：`python test_server.py`
- [ ] 集成到你的应用

## 🌟 为什么使用这个？

1. **快速**：对于 numpy 数组比 JSON 快 10-50 倍
2. **简单**：易于集成和自定义
3. **灵活**：支持任意 Python 对象
4. **健壮**：自动重试和错误处理
5. **生产就绪**：Docker 支持，完整文档

---

**祝编码愉快！🚀**
