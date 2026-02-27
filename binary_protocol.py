import pickle
import numpy as np
import logging
from typing import Any

# Use Pickle Protocol 5 (Python 3.8+)
# It supports out-of-band data, which is very efficient for large numpy arrays
# If Python version < 3.8, default protocol is still much faster than JSON
HIGHEST_PROTOCOL = 5
FIX_IMPORTS = False

logging.basicConfig(
    level=logging.INFO,
    format='[%(name)s] [%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S')
logger = logging.getLogger("InferenceServer")


def dict_to_binary(data: Any) -> bytes:
    """
    Serialize mixed objects containing numpy arrays, strings, dicts to binary stream.
    No compression, pursuing ultimate speed.

    Args:
        data: Any Python object (dict, numpy array, etc.)

    Returns:
        bytes: Serialized binary data
    """
    # fix_imports=False ensures better binary compatibility
    # buffer_callback can be used for extreme optimization, but default is fast enough
    return pickle.dumps(data, protocol=HIGHEST_PROTOCOL, fix_imports=FIX_IMPORTS)


def binary_to_dict(data: bytes) -> Any:
    """
    Restore binary stream to original object.

    Args:
        data: Binary data from dict_to_binary()

    Returns:
        Any: Deserialized Python object
    """
    return pickle.loads(data, fix_imports=FIX_IMPORTS)


# Simple self-test
if __name__ == "__main__":
    test_data = {
        "instruction": "pick up the cup",
        "state": np.array([0.1, 0.2, 0.3], dtype=np.float32),
        "image1": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        "image2": np.random.random((1, 3, 480, 640)).astype(np.float32),
        "image3": np.random.random((1, 3, 480, 640)).astype(np.float32),
        "image4": np.random.random((1, 3, 480, 640)).astype(np.float32),
    }

    import time
    start = time.time()
    blob = dict_to_binary(test_data)
    t1 = time.time() - start

    start = time.time()
    restored = binary_to_dict(blob)
    t2 = time.time() - start

    print(f"Serialize time: {t1*1000:.2f} ms, Size: {len(blob)/1024:.2f} KB")
    print(f"Deserialize time: {t2*1000:.2f} ms")
    for k in test_data.keys():
        if isinstance(test_data[k], np.ndarray):
            print(f"{k}: {test_data[k].shape} -> {restored[k].shape}, "
                  f"Data integrity: {np.array_equal(test_data[k], restored[k])}")
        else:
            print(f"{k}: {test_data[k]} -> {restored[k]}")
