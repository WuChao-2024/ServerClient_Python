#!/usr/bin/env python3
"""
Example usage of the Fast Inference Server.

This script demonstrates how to:
1. Start a server
2. Send inference requests
3. Update model dynamically
"""

import numpy as np
import time
from request_tools import send_inference_request


def example_basic_inference():
    """
    Example 1: Basic inference request
    """
    print("\n" + "="*60)
    print("Example 1: Basic Inference Request")
    print("="*60)

    # Prepare input data
    data = {
        "instruction": "pick up the red cup",
        "state": np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6], dtype=np.float32),
        "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    }

    print("\nInput data:")
    for k, v in data.items():
        if isinstance(v, np.ndarray):
            print(f"  {k}: shape={v.shape}, dtype={v.dtype}")
        else:
            print(f"  {k}: {v}")

    # Send request
    try:
        result = send_inference_request(
            data_dict=data,
            url='http://127.0.0.1:50000/infer',
            timeout=10
        )
        print("\n✓ Success!")
        print("Output:", result)
    except Exception as e:
        print(f"\n✗ Failed: {e}")


def example_batch_inference():
    """
    Example 2: Multiple inference requests
    """
    print("\n" + "="*60)
    print("Example 2: Batch Inference (Sequential)")
    print("="*60)

    num_requests = 5
    total_time = 0

    for i in range(num_requests):
        data = {
            "instruction": f"task {i}",
            "state": np.random.randn(6).astype(np.float32),
            "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        }

        try:
            start = time.time()
            result = send_inference_request(
                data_dict=data,
                url='http://127.0.0.1:50000/infer',
                timeout=10
            )
            elapsed = time.time() - start
            total_time += elapsed
            print(f"Request {i+1}/{num_requests}: {elapsed*1000:.2f} ms")
        except Exception as e:
            print(f"Request {i+1}/{num_requests} failed: {e}")

    print(f"\nTotal time: {total_time*1000:.2f} ms")
    print(f"Average time per request: {total_time/num_requests*1000:.2f} ms")


def example_large_data():
    """
    Example 3: Large data transfer
    """
    print("\n" + "="*60)
    print("Example 3: Large Data Transfer")
    print("="*60)

    # Create large data (multiple high-resolution images)
    data = {
        "instruction": "complex task",
        "state": np.random.randn(100).astype(np.float32),
        "image1": np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8),
        "image2": np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8),
        "image3": np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8),
    }

    # Calculate data size
    total_size = sum(v.nbytes if isinstance(v, np.ndarray) else 0
                     for v in data.values())
    print(f"\nTotal data size: {total_size / 1024 / 1024:.2f} MB")

    try:
        start = time.time()
        result = send_inference_request(
            data_dict=data,
            url='http://127.0.0.1:50000/infer',
            timeout=30
        )
        elapsed = time.time() - start
        print(f"\n✓ Transfer completed in {elapsed*1000:.2f} ms")
        print(f"Throughput: {total_size / elapsed / 1024 / 1024:.2f} MB/s")
    except Exception as e:
        print(f"\n✗ Failed: {e}")


def example_error_handling():
    """
    Example 4: Error handling and retry
    """
    print("\n" + "="*60)
    print("Example 4: Error Handling")
    print("="*60)

    data = {"test": "data"}

    # Test with wrong URL (will trigger retry)
    print("\nTesting with wrong URL (will retry 3 times)...")
    try:
        result = send_inference_request(
            data_dict=data,
            url='http://127.0.0.1:99999/infer',  # Wrong port
            timeout=2,
            max_retries=2,
            retry_delay=0.5
        )
    except Exception as e:
        print(f"✓ Correctly caught error: {type(e).__name__}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Fast Inference Server - Usage Examples")
    print("="*60)
    print("\nMake sure the server is running:")
    print("  python server.py --model-path /path/to/model --device cpu --port 50000")
    print("\nPress Enter to continue...")
    input()

    # Run examples
    example_basic_inference()
    example_batch_inference()
    example_large_data()
    example_error_handling()

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60 + "\n")
