#!/usr/bin/env python3
"""
Installation verification script.
Run this after installing to verify everything works correctly.
"""

import sys
import importlib


def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"  ✗ Python {version.major}.{version.minor} detected")
        print(f"  ✗ Python 3.8 or higher is required")
        return False
    print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Check if all dependencies are installed."""
    print("\nChecking dependencies...")

    dependencies = [
        ('flask', 'Flask'),
        ('torch', 'PyTorch'),
        ('numpy', 'NumPy'),
        ('requests', 'requests'),
    ]

    all_ok = True
    for module_name, display_name in dependencies:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"  ✓ {display_name}: {version}")
        except ImportError:
            print(f"  ✗ {display_name}: not installed")
            all_ok = False

    return all_ok


def check_imports():
    """Check if project modules can be imported."""
    print("\nChecking project modules...")

    modules = [
        'binary_protocol',
        'request_tools',
        'tools',
        'server',
    ]

    all_ok = True
    for module_name in modules:
        try:
            importlib.import_module(module_name)
            print(f"  ✓ {module_name}")
        except ImportError as e:
            print(f"  ✗ {module_name}: {e}")
            all_ok = False

    return all_ok


def test_serialization():
    """Test binary protocol."""
    print("\nTesting serialization...")

    try:
        import numpy as np
        from binary_protocol import dict_to_binary, binary_to_dict

        # Test data
        test_data = {
            "string": "test",
            "number": 42,
            "array": np.array([1, 2, 3], dtype=np.float32),
            "image": np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8),
        }

        # Serialize
        binary = dict_to_binary(test_data)
        print(f"  ✓ Serialization: {len(binary)} bytes")

        # Deserialize
        restored = binary_to_dict(binary)
        print(f"  ✓ Deserialization: {len(restored)} keys")

        # Verify
        if np.array_equal(test_data['array'], restored['array']):
            print(f"  ✓ Data integrity verified")
            return True
        else:
            print(f"  ✗ Data integrity check failed")
            return False

    except Exception as e:
        print(f"  ✗ Serialization test failed: {e}")
        return False


def print_summary(results):
    """Print summary of checks."""
    print("\n" + "=" * 60)
    print("Installation Verification Summary")
    print("=" * 60)

    all_passed = all(results.values())

    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check}")

    print("=" * 60)

    if all_passed:
        print("\n✓ All checks passed! Installation is successful.")
        print("\nNext steps:")
        print("  1. Prepare your model")
        print("  2. Start server: python server.py --model-path /path/to/model")
        print("  3. Test server: python test_server.py")
        print("\nFor more information, see README.md")
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("  - Install missing dependencies: pip install -r requirements.txt")
        print("  - Check Python version: python --version")
        print("  - Verify installation: pip list")

    return all_passed


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Fast Inference Server - Installation Verification")
    print("=" * 60)

    results = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Project Modules": check_imports(),
        "Serialization": test_serialization(),
    }

    success = print_summary(results)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
