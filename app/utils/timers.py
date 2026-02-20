"""Timing utilities for performance monitoring."""

import time
from contextlib import contextmanager
from typing import Generator

from app.utils.logger import get_logger

logger = get_logger(__name__)


@contextmanager
def timer(name: str) -> Generator[None, None, None]:
    """Context manager to time code execution."""
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        elapsed = end - start
        logger.info(f"Execution time for '{name}'", elapsed_seconds=elapsed)


def timeit(func):
    """Decorator to time function execution."""
    def wrapper(*args, **kwargs):
        with timer(func.__name__):
            return func(*args, **kwargs)
    return wrapper
