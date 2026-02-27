#!/usr/bin/env python3
"""
Performance profiler for Fast Inference Server.
Helps identify bottlenecks in your inference pipeline.
"""

import time
import cProfile
import pstats
import io
import numpy as np
from typing import Dict, Any
from binary_protocol import dict_to_binary, binary_to_dict


class PerformanceProfiler:
    """Profile different components of the inference pipeline."""

    def __init__(self):
        self.results = {}

    def profile_serialization(self, data: Dict[str, Any], iterations: int = 100):
        """Profile serialization performance."""
        print("\n" + "=" * 60)
        print("Profiling Serialization")
        print("=" * 60)

        # Calculate data size
        total_size = sum(v.nbytes if isinstance(v, np.ndarray) else 0
                        for v in data.values())
        print(f"\nData size: {total_size / 1024 / 1024:.2f} MB")

        # Profile serialization
        times = []
        for _ in range(iterations):
            start = time.time()
            binary = dict_to_binary(data)
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        throughput = total_size / avg_time / 1024 / 1024

        print(f"\nSerialization ({iterations} iterations):")
        print(f"  Average: {avg_time * 1000:.2f} ms")
        print(f"  Min: {min_time * 1000:.2f} ms")
        print(f"  Max: {max_time * 1000:.2f} ms")
        print(f"  Throughput: {throughput:.2f} MB/s")
        print(f"  Binary size: {len(binary) / 1024 / 1024:.2f} MB")

        self.results['serialization'] = {
            'avg_ms': avg_time * 1000,
            'throughput_mbs': throughput
        }

        # Profile deserialization
        times = []
        for _ in range(iterations):
            start = time.time()
            restored = binary_to_dict(binary)
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        throughput = total_size / avg_time / 1024 / 1024

        print(f"\nDeserialization ({iterations} iterations):")
        print(f"  Average: {avg_time * 1000:.2f} ms")
        print(f"  Min: {min_time * 1000:.2f} ms")
        print(f"  Max: {max_time * 1000:.2f} ms")
        print(f"  Throughput: {throughput:.2f} MB/s")

        self.results['deserialization'] = {
            'avg_ms': avg_time * 1000,
            'throughput_mbs': throughput
        }

    def profile_numpy_to_torch(self, data: Dict[str, Any], device: str = 'cpu'):
        """Profile numpy to torch conversion."""
        print("\n" + "=" * 60)
        print(f"Profiling Numpy → Torch Conversion (device={device})")
        print("=" * 60)

        import torch

        device_obj = torch.device(device)
        iterations = 100

        # Test different conversion methods
        methods = {
            'basic': lambda arr: torch.from_numpy(arr).to(device_obj),
            'pin_memory': lambda arr: torch.from_numpy(arr).pin_memory().to(device_obj, non_blocking=True),
            'contiguous': lambda arr: torch.from_numpy(np.ascontiguousarray(arr)).to(device_obj),
        }

        for name, method in methods.items():
            times = []
            for _ in range(iterations):
                test_array = np.random.randn(1000, 1000).astype(np.float32)
                start = time.time()
                tensor = method(test_array)
                if device_obj.type == 'cuda':
                    torch.cuda.synchronize()
                times.append(time.time() - start)

            avg_time = sum(times) / len(times)
            print(f"\n{name}:")
            print(f"  Average: {avg_time * 1000:.2f} ms")

    def profile_with_cprofile(self, func, *args, **kwargs):
        """Profile function with cProfile."""
        print("\n" + "=" * 60)
        print("Detailed Profiling with cProfile")
        print("=" * 60)

        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()

        # Print stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(20)
        print(s.getvalue())

        return result

    def generate_report(self):
        """Generate performance report."""
        print("\n" + "=" * 60)
        print("Performance Report Summary")
        print("=" * 60)

        if 'serialization' in self.results:
            print(f"\nSerialization:")
            print(f"  Latency: {self.results['serialization']['avg_ms']:.2f} ms")
            print(f"  Throughput: {self.results['serialization']['throughput_mbs']:.2f} MB/s")

        if 'deserialization' in self.results:
            print(f"\nDeserialization:")
            print(f"  Latency: {self.results['deserialization']['avg_ms']:.2f} ms")
            print(f"  Throughput: {self.results['deserialization']['throughput_mbs']:.2f} MB/s")

        print("\n" + "=" * 60)


def main():
    """Run profiling."""
    print("=" * 60)
    print("Fast Inference Server - Performance Profiler")
    print("=" * 60)

    profiler = PerformanceProfiler()

    # Test data
    test_data = {
        "instruction": "test instruction",
        "state": np.random.randn(100).astype(np.float32),
        "image1": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        "image2": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    }

    # Profile serialization
    profiler.profile_serialization(test_data, iterations=100)

    # Profile numpy to torch conversion
    try:
        import torch
        if torch.cuda.is_available():
            profiler.profile_numpy_to_torch(test_data, device='cuda:0')
        profiler.profile_numpy_to_torch(test_data, device='cpu')
    except ImportError:
        print("\nSkipping torch profiling (PyTorch not available)")

    # Generate report
    profiler.generate_report()

    print("\n" + "=" * 60)
    print("Profiling completed!")
    print("=" * 60)
    print("\nOptimization tips:")
    print("  1. Use C-contiguous numpy arrays")
    print("  2. Use float32 instead of float64")
    print("  3. Enable pin_memory for GPU transfer")
    print("  4. Use torch.inference_mode() for inference")
    print("  5. Consider model compilation (torch.jit or torch.compile)")
    print()


if __name__ == "__main__":
    main()
