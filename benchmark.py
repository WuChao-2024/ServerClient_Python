#!/usr/bin/env python3
"""
Benchmark script for Fast Inference Server.

This script measures:
- Serialization/deserialization performance
- Network transfer speed
- End-to-end latency
- Throughput under different data sizes
"""

import time
import numpy as np
import sys
from typing import List, Tuple
from binary_protocol import dict_to_binary, binary_to_dict
from request_tools import send_inference_request


def benchmark_serialization(data_sizes: List[Tuple[str, dict]]):
    """
    Benchmark serialization performance.

    Args:
        data_sizes: List of (name, data) tuples to benchmark
    """
    print("\n" + "=" * 60)
    print("Benchmark 1: Serialization Performance")
    print("=" * 60)

    for name, data in data_sizes:
        # Calculate data size
        total_size = sum(v.nbytes if isinstance(v, np.ndarray) else 0
                        for v in data.values())

        # Benchmark serialization
        times = []
        for _ in range(10):
            start = time.time()
            binary = dict_to_binary(data)
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        throughput = total_size / avg_time / 1024 / 1024

        print(f"\n{name}:")
        print(f"  Data size: {total_size / 1024 / 1024:.2f} MB")
        print(f"  Binary size: {len(binary) / 1024 / 1024:.2f} MB")
        print(f"  Serialize time: {avg_time * 1000:.2f} ms")
        print(f"  Throughput: {throughput:.2f} MB/s")

        # Benchmark deserialization
        times = []
        for _ in range(10):
            start = time.time()
            restored = binary_to_dict(binary)
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        throughput = total_size / avg_time / 1024 / 1024

        print(f"  Deserialize time: {avg_time * 1000:.2f} ms")
        print(f"  Throughput: {throughput:.2f} MB/s")


def benchmark_end_to_end(url: str, data_sizes: List[Tuple[str, dict]]):
    """
    Benchmark end-to-end latency.

    Args:
        url: Server URL
        data_sizes: List of (name, data) tuples to benchmark
    """
    print("\n" + "=" * 60)
    print("Benchmark 2: End-to-End Latency")
    print("=" * 60)

    for name, data in data_sizes:
        total_size = sum(v.nbytes if isinstance(v, np.ndarray) else 0
                        for v in data.values())

        print(f"\n{name} ({total_size / 1024 / 1024:.2f} MB):")

        # Warmup
        try:
            send_inference_request(data, url=url, timeout=30, max_retries=0)
        except:
            print("  ✗ Server not available")
            continue

        # Benchmark
        times = []
        for i in range(10):
            try:
                start = time.time()
                result = send_inference_request(data, url=url, timeout=30, max_retries=0)
                elapsed = time.time() - start
                times.append(elapsed)
            except Exception as e:
                print(f"  Request {i+1} failed: {e}")
                break

        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            throughput = total_size / avg_time / 1024 / 1024

            print(f"  Average: {avg_time * 1000:.2f} ms")
            print(f"  Min: {min_time * 1000:.2f} ms")
            print(f"  Max: {max_time * 1000:.2f} ms")
            print(f"  Throughput: {throughput:.2f} MB/s")


def benchmark_sustained_load(url: str, duration: int = 10):
    """
    Benchmark sustained load.

    Args:
        url: Server URL
        duration: Test duration in seconds
    """
    print("\n" + "=" * 60)
    print(f"Benchmark 3: Sustained Load ({duration}s)")
    print("=" * 60)

    data = {
        "instruction": "sustained load test",
        "state": np.random.randn(10).astype(np.float32),
        "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    }

    start_time = time.time()
    request_count = 0
    errors = 0
    times = []

    print("\nRunning...")

    while time.time() - start_time < duration:
        try:
            req_start = time.time()
            result = send_inference_request(data, url=url, timeout=10, max_retries=0)
            req_time = time.time() - req_start
            times.append(req_time)
            request_count += 1
        except Exception as e:
            errors += 1

    total_time = time.time() - start_time

    print(f"\nResults:")
    print(f"  Total requests: {request_count}")
    print(f"  Errors: {errors}")
    print(f"  Success rate: {request_count / (request_count + errors) * 100:.1f}%")
    print(f"  Requests/sec: {request_count / total_time:.2f}")

    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        print(f"  Average latency: {avg_time * 1000:.2f} ms")
        print(f"  Min latency: {min_time * 1000:.2f} ms")
        print(f"  Max latency: {max_time * 1000:.2f} ms")


def main():
    """Run all benchmarks."""
    print("=" * 60)
    print("Fast Inference Server - Performance Benchmark")
    print("=" * 60)

    # Define test data sizes
    data_sizes = [
        ("Small (VGA image)", {
            "instruction": "test",
            "state": np.random.randn(10).astype(np.float32),
            "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        }),
        ("Medium (HD image)", {
            "instruction": "test",
            "state": np.random.randn(50).astype(np.float32),
            "image": np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8),
        }),
        ("Large (Full HD image)", {
            "instruction": "test",
            "state": np.random.randn(100).astype(np.float32),
            "image": np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8),
        }),
        ("Extra Large (Multiple Full HD)", {
            "instruction": "test",
            "state": np.random.randn(100).astype(np.float32),
            "image1": np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8),
            "image2": np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8),
            "image3": np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8),
        }),
    ]

    # Run benchmarks
    benchmark_serialization(data_sizes)

    # Check if server is available
    url = 'http://127.0.0.1:50000/infer'
    if len(sys.argv) > 1:
        url = sys.argv[1]

    print(f"\n\nChecking server at {url}...")
    try:
        test_data = data_sizes[0][1]
        send_inference_request(test_data, url=url, timeout=5, max_retries=0)
        print("✓ Server is available")

        benchmark_end_to_end(url, data_sizes)
        benchmark_sustained_load(url, duration=10)

    except Exception as e:
        print(f"✗ Server not available: {e}")
        print("\nSkipping server benchmarks.")
        print("To run full benchmarks, start the server:")
        print("  python server.py --model-path /path/to/model --device cpu --port 50000")

    print("\n" + "=" * 60)
    print("Benchmark completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
