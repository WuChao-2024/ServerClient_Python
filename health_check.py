#!/usr/bin/env python3
"""
Quick health check script for Fast Inference Server.
"""

import sys
import requests
import time


def check_server_health(url='http://127.0.0.1:50000', timeout=5):
    """
    Check if server is running and healthy.

    Args:
        url: Server base URL
        timeout: Request timeout in seconds

    Returns:
        bool: True if server is healthy, False otherwise
    """
    print(f"Checking server health at {url}...")

    try:
        # Try to connect to server
        start_time = time.time()
        response = requests.get(f"{url}/health", timeout=timeout)
        elapsed = time.time() - start_time

        if response.status_code == 200:
            print(f"✓ Server is healthy (response time: {elapsed*1000:.2f} ms)")
            return True
        else:
            print(f"✗ Server returned status code: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to server at {url}")
        print(f"  Make sure the server is running:")
        print(f"  python server.py --model-path /path/to/model --device cpu --port 50000")
        return False

    except requests.exceptions.Timeout:
        print(f"✗ Server request timed out after {timeout} seconds")
        return False

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description='Health check for Fast Inference Server')
    parser.add_argument('--url', type=str, default='http://127.0.0.1:50000',
                        help='Server URL (default: http://127.0.0.1:50000)')
    parser.add_argument('--timeout', type=int, default=5,
                        help='Request timeout in seconds (default: 5)')
    args = parser.parse_args()

    healthy = check_server_health(args.url, args.timeout)
    sys.exit(0 if healthy else 1)


if __name__ == "__main__":
    main()
