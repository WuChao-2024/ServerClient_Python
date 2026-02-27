import time
import requests
import numpy as np
from typing import Optional, Dict, Any

from binary_protocol import dict_to_binary, binary_to_dict


def send_inference_request(
    data_dict: Dict[str, Any],
    url: str = 'http://127.0.0.1:50000/infer',
    timeout: int = 10,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Dict[str, Any]:
    """
    Send inference request using binary Pickle protocol with timeout and auto-retry support.
    Compatible with Python 3.8+ and Numpy 2.x.

    Args:
        data_dict: Input data dictionary (can contain numpy arrays)
        url: Inference service URL
        timeout: Single HTTP request timeout (seconds)
        max_retries: Maximum number of retries
        retry_delay: Wait time before retry (seconds)

    Returns:
        Dict[str, Any]: Decoded response dictionary (contains numpy arrays)

    Raises:
        RuntimeError: If max retries exceeded or non-200 response received
    """
    # 1. Try to serialize input data
    try:
        req_body = dict_to_binary(data_dict)
    except Exception as e:
        raise RuntimeError(f"Failed to serialize request data: {e}")

    # 2. Set binary stream headers
    headers = {
        'Content-Type': 'application/octet-stream'
    }

    # 3. Send binary stream with retry logic
    last_exception: Optional[Exception] = None
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, data=req_body, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                try:
                    result_dict = binary_to_dict(resp.content)
                    return result_dict
                except Exception as deserialize_err:
                    raise RuntimeError(f"Failed to deserialize response: {deserialize_err}")
            else:
                error_msg = f"HTTP {resp.status_code}"
                try:
                    err_data = binary_to_dict(resp.content)
                    if isinstance(err_data, dict) and "message" in err_data:
                        error_msg += f": {err_data['message']}"
                    else:
                        error_msg += f": {resp.text[:200]}"
                except:
                    error_msg += f": {resp.text[:200]}"
                print(f"[Attempt {attempt + 1}/{max_retries + 1}] Server error: {error_msg}")
                last_exception = RuntimeError(error_msg)

        except requests.exceptions.Timeout as e:
            last_exception = e
            print(f"[Attempt {attempt + 1}/{max_retries + 1}] Request timeout: {e}")

        except requests.exceptions.ConnectionError as e:
            last_exception = e
            print(f"[Attempt {attempt + 1}/{max_retries + 1}] Connection error: {e}")

        except requests.exceptions.RequestException as e:
            last_exception = e
            print(f"[Attempt {attempt + 1}/{max_retries + 1}] Network error: {e}")

        except Exception as e:
            last_exception = e
            print(f"[Attempt {attempt + 1}/{max_retries + 1}] Unexpected error: {e}")

        # Wait before retry if not the last attempt
        if attempt < max_retries:
            time.sleep(retry_delay)

    raise RuntimeError(f"Failed after {max_retries + 1} attempts. Last error: {last_exception}")


def main():
    """
    Test function for inference request.
    """
    print("=" * 60)
    print("Testing Inference Request")
    print("=" * 60)

    # Prepare test data
    test_data = {
        "instruction": "pick up the red cup",
        "state": np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6], dtype=np.float32),
        "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    }

    print("\nTest data prepared:")
    for k, v in test_data.items():
        if isinstance(v, np.ndarray):
            print(f"  {k}: shape={v.shape}, dtype={v.dtype}")
        else:
            print(f"  {k}: {v}")

    # Send request
    print(f"\nSending request to http://127.0.0.1:50000/infer ...")
    try:
        start_time = time.time()
        result = send_inference_request(
            data_dict=test_data,
            url='http://127.0.0.1:50000/infer',
            timeout=10,
            max_retries=3
        )
        elapsed_time = time.time() - start_time

        print(f"\n✓ Request successful! (took {elapsed_time*1000:.2f} ms)")
        print("\nResponse:")
        for k, v in result.items():
            if isinstance(v, np.ndarray):
                print(f"  {k}: shape={v.shape}, dtype={v.dtype}")
            else:
                print(f"  {k}: {v}")

    except RuntimeError as e:
        print(f"\n✗ Request failed: {e}")
        print("\nPlease make sure the server is running:")
        print("  python server.py --model-path /path/to/model --device cpu --port 50000")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
