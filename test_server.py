#!/usr/bin/env python3
"""
Quick test script to verify server is working correctly.
"""

import sys
import time
import numpy as np
from request_tools import send_inference_request


def test_server(url='http://127.0.0.1:50000/infer'):
    """
    Test if server is responding correctly.

    Args:
        url: Server URL to test
    """
    print("=" * 60)
    print("Testing Fast Inference Server")
    print("=" * 60)
    print(f"\nServer URL: {url}")

    # Prepare test data
    test_data = {
        "instruction": "test instruction",
        "state": np.array([0.1, 0.2, 0.3], dtype=np.float32),
        "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    }

    print("\nTest data prepared:")
    print(f"  - instruction: string")
    print(f"  - state: shape={test_data['state'].shape}, dtype={test_data['state'].dtype}")
    print(f"  - image: shape={test_data['image'].shape}, dtype={test_data['image'].dtype}")

    # Test connection
    print("\n" + "-" * 60)
    print("Test 1: Basic Connection")
    print("-" * 60)

    try:
        start_time = time.time()
        result = send_inference_request(
            data_dict=test_data,
            url=url,
            timeout=10,
            max_retries=1
        )
        elapsed = time.time() - start_time

        print(f"✓ Connection successful!")
        print(f"  Response time: {elapsed*1000:.2f} ms")
        print(f"  Status: {result.get('status', 'unknown')}")

        if 'output' in result:
            output = result['output']
            if isinstance(output, np.ndarray):
                print(f"  Output shape: {output.shape}")
                print(f"  Output dtype: {output.dtype}")

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nPlease make sure the server is running:")
        print(f"  python server.py --model-path /path/to/model --device cpu --port 50000")
        return False

    # Test multiple requests
    print("\n" + "-" * 60)
    print("Test 2: Multiple Requests (Sequential)")
    print("-" * 60)

    num_requests = 5
    times = []

    for i in range(num_requests):
        try:
            start_time = time.time()
            result = send_inference_request(
                data_dict=test_data,
                url=url,
                timeout=10,
                max_retries=1
            )
            elapsed = time.time() - start_time
            times.append(elapsed)
            print(f"  Request {i+1}/{num_requests}: {elapsed*1000:.2f} ms")
        except Exception as e:
            print(f"  Request {i+1}/{num_requests}: Failed - {e}")
            return False

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"\n  Average: {avg_time*1000:.2f} ms")
    print(f"  Min: {min_time*1000:.2f} ms")
    print(f"  Max: {max_time*1000:.2f} ms")

    # Test large data
    print("\n" + "-" * 60)
    print("Test 3: Large Data Transfer")
    print("-" * 60)

    large_data = {
        "instruction": "large data test",
        "state": np.random.randn(100).astype(np.float32),
        "image1": np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8),
        "image2": np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8),
    }

    data_size = sum(v.nbytes if isinstance(v, np.ndarray) else 0
                    for v in large_data.values())
    print(f"  Data size: {data_size / 1024 / 1024:.2f} MB")

    try:
        start_time = time.time()
        result = send_inference_request(
            data_dict=large_data,
            url=url,
            timeout=30,
            max_retries=1
        )
        elapsed = time.time() - start_time
        throughput = data_size / elapsed / 1024 / 1024

        print(f"✓ Large data transfer successful!")
        print(f"  Transfer time: {elapsed*1000:.2f} ms")
        print(f"  Throughput: {throughput:.2f} MB/s")

    except Exception as e:
        print(f"✗ Large data transfer failed: {e}")
        return False

    # Summary
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    print("\nServer is working correctly.")
    print(f"Average latency: {avg_time*1000:.2f} ms")
    print(f"Throughput: {throughput:.2f} MB/s")
    print()

    return True


if __name__ == "__main__":
    # Parse command line arguments
    url = 'http://127.0.0.1:50000/infer'
    if len(sys.argv) > 1:
        url = sys.argv[1]

    success = test_server(url)
    sys.exit(0 if success else 1)
