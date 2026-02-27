# Copyright (c) 2025, Cauchy WuChao, D-Robotics.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
os.environ["CUDA_VISIBLE_DEVICES"] = "7"


import json
import gzip
import numpy as np
import torch
import requests
import logging
import argparse
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
import random
import copy

from base64_tools import serialize_dict, deserialize_dict

logging.basicConfig(
    level = logging.INFO,
    format = '[%(name)s] [%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S')
logger = logging.getLogger("SmolVLA_Server")

def send_inference_request(data_dict, url='http://127.0.0.1:50001/infer', compressed: bool = False, device: torch.device = torch.device('cpu')):
    """
    发送推理请求
    :param data_dict: dict, key=str, value=str or np.ndarray
    :param url: 服务地址
    :param compressed: bool, 是否对 *请求体* 启用 gzip 压缩
    :return: dict, 解码后的响应数据
    """
    # 准备请求体
    resp_bytes = json.dumps(serialize_dict(data_dict)).encode('utf-8')
    body = gzip.compress(resp_bytes) if compressed else resp_bytes
    headers = {'Content-Type': 'application/json'}
    headers['compressed'] = 'gzip' if compressed else 'raw'
    # 发送请求
    resp = requests.post(url, data=body, headers=headers)
    # 检查 HTTP 状态
    if resp.status_code != 200:
        raise RuntimeError(f"Server returned {resp.status_code}: {resp.text}")
    content_encoding = resp.headers.get('compressed', '').lower()
    raw_data = gzip.decompress(resp.content) if content_encoding == 'gzip' else resp.content
    decoded_result = deserialize_dict(json.loads(raw_data.decode('utf-8')), device=device)
    return decoded_result


from tqdm import tqdm

def cosine_similarity(A, B):
    # 将张量展平为一维向量
    A_flat = A.flatten()
    B_flat = B.flatten()
    # 计算点积和范数
    dot_product = np.dot(A_flat, B_flat)
    norm_A = np.linalg.norm(A_flat)
    norm_B = np.linalg.norm(B_flat)
    # 避免除以零
    if norm_A == 0 or norm_B == 0:
        return 0
    cos = dot_product / (norm_A * norm_B)
    error = A - B
    mse = np.mean((A - B) ** 2)
    return (cos, mse)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--smolvla-path', type=str, default="../LeRobot_Cloud/train_result_aloha-agilex_clean_50_adjust_bottle/checkpoints/100000/pretrained_model", help="")
    parser.add_argument("--lerobot-dataset-path", type=str, default="/home/chao.wu/SmolVLA_RoboTwin2_BPU/huggingface/lerobot/adjust_bottle_aloha-agilex_clean_50_image", help="", )
    parser.add_argument('--device', type=str, default="cuda:0", help="")
    parser.add_argument('--port', type=int, default=50001, help="")
    opt = parser.parse_args()
    logger.info(opt)

    device = torch.device(opt.device)
    # 构造测试数据
    datas = LeRobotDataset(repo_id="Foo/Bar", root=opt.lerobot_dataset_path,)
    print(f"{len(datas) = }")
    
    # 本地加载policy
    policy = SmolVLAPolicy.from_pretrained(opt.smolvla_path).to(device).eval()
    

    # 随机选择 100 个不重复的索引（如果数据集小于100，则选全部）
    coses = []
    msees = []
    result_str_coses = ""
    result_str_coses += "| cos: mean (min ~ max), 1%%low  | mse: mean (min ~ max), 1%%high |\n"
    result_str_coses += "|--------------------------------|--------------------------------|\n"
    
    # 不压缩测试
    num_samples = min(100, len(datas))
    indices = random.sample(range(len(datas)), num_samples)
    for idx in tqdm(indices, desc="Processing samples", ncols=80):
        data = datas[idx]
        obs = {}
        obs["instruction"] = data['task']  # str
        obs["task"] = obs['instruction']
        obs['observation.images.cam_high'] = data['observation.images.cam_high'].unsqueeze(0)
        obs['observation.images.cam_left_wrist'] = data['observation.images.cam_left_wrist'].unsqueeze(0)
        obs['observation.images.cam_right_wrist'] = data['observation.images.cam_right_wrist'].unsqueeze(0)
        obs['observation.state'] = data['action'].unsqueeze(0)

        # 不压缩
        out_uncompressed = send_inference_request(copy.deepcopy(obs), compressed=False, device=device)['action_chunk']

        # Truth
        obs = {}
        obs["instruction"] = data['task']  # str
        obs["task"] = obs['instruction']
        obs['observation.images.cam_high'] = data['observation.images.cam_high'].unsqueeze(0).to(device)
        obs['observation.images.cam_left_wrist'] = data['observation.images.cam_left_wrist'].unsqueeze(0).to(device)
        obs['observation.images.cam_right_wrist'] = data['observation.images.cam_right_wrist'].unsqueeze(0).to(device)
        obs['observation.state'] = data['action'].unsqueeze(0).to(device)
            
        action_chunk = policy.predict_action_chunk(copy.deepcopy(obs)).detach().cpu().numpy()
        cos, mse = cosine_similarity(action_chunk, out_uncompressed)
        coses.append(cos)
        msees.append(mse)
    coses, mses = np.array(coses), np.array(msees)
    result_str_coses += f"| actions | {np.mean(coses):.3f} ( {coses.min():.3f} ~ {coses.max():.3f} ), {np.percentile(coses, 1):.3f} | {np.mean(mses):.3f} ( {mses.min():.3f} ~ {mses.max():.3f} ), {np.percentile(mses, 99):.3f} | \n"
    print(result_str_coses)
    # 压缩测试
    coses = []
    msees = []
    num_samples = min(100, len(datas))
    indices = random.sample(range(len(datas)), num_samples)
    for idx in tqdm(indices, desc="Processing samples", ncols=80):
        data = datas[idx]
        obs = {}
        obs["instruction"] = data['task']  # str
        obs["task"] = obs['instruction']
        obs['observation.images.cam_high'] = data['observation.images.cam_high'].unsqueeze(0)
        obs['observation.images.cam_left_wrist'] = data['observation.images.cam_left_wrist'].unsqueeze(0)
        obs['observation.images.cam_right_wrist'] = data['observation.images.cam_right_wrist'].unsqueeze(0)
        obs['observation.state'] = data['action'].unsqueeze(0)

        # 不压缩
        # out_uncompressed = send_inference_request(copy.deepcopy(obs), compressed=False, device=device)
        out_compressed = send_inference_request(copy.deepcopy(obs), compressed=True, device=device)['action_chunk']

        # Truth
        obs = {}
        obs["instruction"] = data['task']  # str
        obs["task"] = obs['instruction']
        obs['observation.images.cam_high'] = data['observation.images.cam_high'].unsqueeze(0).to(device)
        obs['observation.images.cam_left_wrist'] = data['observation.images.cam_left_wrist'].unsqueeze(0).to(device)
        obs['observation.images.cam_right_wrist'] = data['observation.images.cam_right_wrist'].unsqueeze(0).to(device)
        obs['observation.state'] = data['action'].unsqueeze(0).to(device)
            
        action_chunk = policy.predict_action_chunk(copy.deepcopy(obs)).detach().cpu().numpy()
        cos, mse = cosine_similarity(action_chunk, out_compressed)
        coses.append(cos)
        msees.append(mse)
    coses, mses = np.array(coses), np.array(msees)
    result_str_coses += f"| actions | {np.mean(coses):.3f} ( {coses.min():.3f} ~ {coses.max():.3f} ), {np.percentile(coses, 1):.3f} | {np.mean(mses):.3f} ( {mses.min():.3f} ~ {mses.max():.3f} ), {np.percentile(mses, 99):.3f} | \n"
    
    print(result_str_coses)
    exit()
    data = datas[943]
    obs = {}
    obs["instruction"] = data['task']  # str
    obs["task"] = obs['instruction']
    obs['observation.images.cam_high'] = data['observation.images.cam_high'].unsqueeze(0)#.detach().cpu()#.numpy()
    obs['observation.images.cam_left_wrist'] = data['observation.images.cam_left_wrist'].unsqueeze(0)#.detach().cpu()#.numpy()
    obs['observation.images.cam_right_wrist'] = data['observation.images.cam_right_wrist'].unsqueeze(0)#.detach().cpu()#.numpy()
    obs['observation.state'] = data['action'].unsqueeze(0)#.detach().cpu().numpy()

    # 不压缩
    print(send_inference_request(obs, compressed=False, device=device)['action_chunk'].shape)
    print(send_inference_request(obs, compressed=True, device=device)['action_chunk'].shape)