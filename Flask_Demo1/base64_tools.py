import base64
import io
import numpy as np
import torch

def serialize_np(arr: np.ndarray) -> str:
    """将 np.ndarray 序列化为 base64 字符串"""
    buffer = io.BytesIO()
    np.save(buffer, arr, allow_pickle=False)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def deserialize_np(b64_str: str) -> np.ndarray:
    """从 base64 字符串还原 np.ndarray"""
    data = base64.b64decode(b64_str.encode('utf-8'))
    buffer = io.BytesIO(data)
    return np.load(buffer, allow_pickle=False)

def serialize_dict(d: dict) -> dict:
    """将dict中的array/tensor序列化为base64字符串"""
    serialize_d = {}
    for k, v in d.items():
        if isinstance(v, np.ndarray):
            serialize_d[f"base64numpy_{k}"] = serialize_np(v)
        elif isinstance(v, torch.Tensor):
            serialize_d[f"base64torch_{k}"] = serialize_np(v.detach().cpu().numpy())
        else:
            serialize_d[k] = v
    return serialize_d

def deserialize_dict(d: dict, device: torch.device = torch.device('cpu')) -> dict:
    """将dict中的base64字符串还原为array/tensor"""
    deserialize_d = {}
    for k, v in d.items():
        if k.startswith("base64numpy_"):
            deserialize_d[k[12:]] = deserialize_np(v)
        elif k.startswith("base64torch_"):
            deserialize_d[k[12:]] = torch.from_numpy(deserialize_np(v)).to(device)
        else:
            deserialize_d[k] = v
    return deserialize_d