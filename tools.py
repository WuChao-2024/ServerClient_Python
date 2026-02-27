import os
from functools import wraps
import time
import numpy as np
import torch


def measure_time(logger):
    """
    Returns a decorator that logs execution time using the specified logger.

    Args:
        logger: Logger instance to use for logging

    Returns:
        decorator: Function decorator that measures execution time
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            begin_time = time.time()
            result = func(*args, **kwargs)
            elapsed_ms = 1000 * (time.time() - begin_time)
            logger.info("\033[1;31m" + f"{func.__name__}: {elapsed_ms:.2f} ms" + "\033[0m")
            return result
        return wrapper
    return decorator


def show_data_summary(data):
    """
    Print summary of data dimensions and types.

    Args:
        data: Dictionary containing numpy arrays or torch tensors
    """
    for k, v in data.items():
        if isinstance(v, np.ndarray):
            print(f"{k}: {v.shape} {v.dtype} {type(v)} {v.min():.4f}~{v.max():.4f}")
        elif isinstance(v, torch.Tensor):
            print(f"{k}: {v.shape} {v.dtype} {type(v)} {v.min():.4f}~{v.max():.4f}")
        else:
            print(f"{k}: {v} {type(v)}")
