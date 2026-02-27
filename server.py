# Copyright (c) 2025, Fast Inference Server Contributors.
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
import argparse
import logging
import time
import torch
import numpy as np
import tempfile
import tarfile
import shutil
from typing import Optional

from tools import measure_time, show_data_summary
from binary_protocol import dict_to_binary, binary_to_dict
from flask import Flask, Response, request

logging.basicConfig(
    level=logging.INFO,
    format='[%(name)s] [%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S')
logger = logging.getLogger("InferenceServer")

app = Flask(__name__)

# Global variables for model and device
global model, device
model = None
device = None


@app.route('/infer', methods=['POST'])
def infer():
    """
    Inference endpoint.

    Accepts binary data (Pickle serialized) and returns inference results.
    """
    global model, device

    # Check if service is ready
    if model is None:
        return Response(
            dict_to_binary({"status": "error", "message": "Service not ready"}),
            status=503,
            mimetype='application/octet-stream'
        )

    try:
        # 1. Deserialize request data
        begin_time = time.time()
        data = binary_to_dict(request.data)
        logger.info(f"Deserialize time = {1000*(time.time() - begin_time):.2f} ms")

        # 2. Prepare observation data
        begin_time = time.time()
        obs = {}
        for k, v in data.items():
            if isinstance(v, np.ndarray):
                # Ensure array is C-contiguous for faster transfer
                if not v.flags['C_CONTIGUOUS']:
                    v = np.ascontiguousarray(v)
                # Convert to torch tensor and move to device
                obs[k] = torch.from_numpy(v).to(device)
            else:
                obs[k] = v
        logger.info(f"Data preparation time = {1000*(time.time() - begin_time):.2f} ms")

        # 3. Model inference
        begin_time = time.time()
        with torch.inference_mode():
            # Replace this with your actual model inference logic
            # Example: output = model(obs)
            output = model_inference(obs)
        logger.info(f"{device} inference time = {1000*(time.time() - begin_time):.2f} ms")

        # 4. Serialize response
        begin_time = time.time()
        response_blob = dict_to_binary({
            "status": "ok",
            "output": output
        })
        logger.info(f"Serialize time = {1000*(time.time() - begin_time):.2f} ms")

        return Response(response_blob, status=200, mimetype='application/octet-stream')

    except Exception as e:
        logger.error(f"Inference error: {e}", exc_info=True)
        return Response(
            dict_to_binary({"status": "error", "message": str(e)}),
            status=500,
            mimetype='application/octet-stream'
        )


@app.route('/update_model', methods=['POST'])
def update_model():
    """
    Update model dynamically without restarting the server.

    Accepts a .tar file containing model files.
    """
    global model, device

    # Get device from form data
    device_str = request.form.get('device', '').strip()
    if device_str:
        device = torch.device(device_str)

    # Check if file is present
    if 'file' not in request.files:
        return {"error": "No file part"}, 400

    file = request.files['file']
    if file.filename == '':
        return {"error": "No selected file"}, 400

    if not file.filename.endswith('.tar'):
        return {"error": "Only .tar (uncompressed archive) is allowed"}, 400

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Extracting uploaded model to: {temp_dir}")

            # Save and extract .tar file
            tar_path = os.path.join(temp_dir, 'uploaded.tar')
            file.save(tar_path)

            with tarfile.open(tar_path, 'r') as tar:
                # Security check: prevent path traversal (CVE-2007-4559)
                def is_within_directory(directory, target):
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    return prefix == abs_directory

                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                    tar.extractall(path, members, numeric_owner=numeric_owner)

                safe_extract(tar, path=temp_dir)

            # Remove tar file, keep extracted content
            os.remove(tar_path)

            # Find actual model directory
            extracted_items = os.listdir(temp_dir)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
                model_dir = os.path.join(temp_dir, extracted_items[0])
            else:
                model_dir = temp_dir

            # Load new model
            logger.info(f"Loading new model from: {model_dir}")
            new_model = load_model(model_dir, device)

            # Replace global model
            model = new_model
            logger.info("Model updated successfully!")

            return {"message": "Model updated successfully"}, 200

    except Exception as e:
        logger.error(f"Failed to update model: {e}", exc_info=True)
        return {"error": str(e)}, 500


def load_model(model_path: str, device: torch.device):
    """
    Load model from path.

    Replace this function with your actual model loading logic.

    Args:
        model_path: Path to model directory
        device: Device to load model on

    Returns:
        Loaded model
    """
    # Example implementation - replace with your actual model loading
    logger.info(f"Loading model from {model_path}")

    # For demonstration, create a simple dummy model
    class DummyModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(10, 10)

        def forward(self, x):
            return self.linear(x)

    model = DummyModel().to(device).eval()

    # In real implementation, you would load from model_path:
    # model = YourModelClass.from_pretrained(model_path).to(device).eval()

    return model


def model_inference(obs: dict) -> np.ndarray:
    """
    Perform model inference.

    Replace this function with your actual inference logic.

    Args:
        obs: Observation dictionary containing input data

    Returns:
        numpy.ndarray: Model output
    """
    global model, device

    # Example implementation - replace with your actual inference
    # For demonstration, return dummy output
    output = np.random.randn(7).astype(np.float32)

    # In real implementation:
    # output = model(obs).detach().cpu().numpy()

    return output


def main():
    parser = argparse.ArgumentParser(description='Fast Inference Server')
    parser.add_argument('--model-path', type=str, required=True,
                        help='Path to model directory')
    parser.add_argument('--device', type=str, default='cpu',
                        help='Device to run inference (e.g., cuda:0, cpu)')
    parser.add_argument('--port', type=int, default=50000,
                        help='Server port')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Server host')
    opt = parser.parse_args()

    logger.info(f"Starting server with config: {opt}")

    # Initialize global variables
    global model, device
    device = torch.device(opt.device)

    # Load model
    logger.info("Loading model...")
    model = load_model(opt.model_path, device)
    logger.info("Model loaded successfully!")

    # Start Flask server (single-threaded for sequential processing)
    logger.info(f"Server starting on {opt.host}:{opt.port}")
    app.run(host=opt.host, port=opt.port, threaded=False, debug=False)


if __name__ == "__main__":
    main()
