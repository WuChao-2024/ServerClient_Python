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
os.environ["CUDA_VISIBLE_DEVICES"] = "5"
import argparse
import logging
import time
import torch
import json
import gzip

from base64_tools import serialize_dict, deserialize_dict
from tools import measure_time, show_data_summary

from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
from flask import Flask, request

logging.basicConfig(
    level = logging.INFO,
    format = '[%(name)s] [%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S')
logger = logging.getLogger("SmolVLA_Server")

app = Flask(__name__)

global smolvla_policy, device
smolvla_policy = None
device = None

@app.route('/infer', methods=['POST'])
def infer():
    global smolvla_policy, device
    compressed = request.headers.get('compressed', '').lower() == 'gzip'
    raw_data = request.get_data()
    try:
        data = decode_request_data(raw_data, compressed=compressed, device=device)
        begin_time = time.time()
        with torch.no_grad():
            action_chunk = smolvla_policy.predict_action_chunk(data).detach().cpu().numpy()#[0,0,:]
        logger.info("\033[1;31m" + f"{device} inference time = {1000*(time.time() - begin_time):.2f} ms" + "\033[0m")
        return encode_request_data({'action_chunk': action_chunk, 'message': 'success'}, compressed=compressed)
    except Exception as e:
        logger.error(e)
        return encode_request_data({'message': 'error'}, compressed=compressed)

@measure_time(logger)
def decode_request_data(raw_data, compressed: bool = False, device: torch.device = torch.device('cpu')):
    raw_data = gzip.decompress(raw_data) if compressed else raw_data
    return deserialize_dict(json.loads(raw_data.decode('utf-8')), device=device)

@measure_time(logger)
def encode_request_data(data: dict, compressed: bool = False):
    resp_bytes = json.dumps(serialize_dict(data)).encode('utf-8')
    resp_bytes = gzip.compress(resp_bytes) if compressed else resp_bytes
    headers = {'Content-Type': 'application/json'}
    headers['compressed'] = 'gzip' if compressed else 'raw'
    return app.response_class(response=resp_bytes, status=200, headers=headers)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smolvla-path', type=str, default="../LeRobot_Cloud/train_result_aloha-agilex_clean_50_adjust_bottle/checkpoints/100000/pretrained_model", help="")
    parser.add_argument('--device', type=str, default="cuda:0", help="")
    parser.add_argument('--port', type=int, default=50001, help="")
    opt = parser.parse_args()
    logger.info(opt)
    
    logger.info("Loading model ...")
    global smolvla_policy, device
    device = torch.device(opt.device)
    smolvla_policy = SmolVLAPolicy.from_pretrained(opt.smolvla_path).to(device).eval()

    app.run(host='0.0.0.0', port=50001, threaded=False, debug=False)

if __name__ == "__main__":
    main()