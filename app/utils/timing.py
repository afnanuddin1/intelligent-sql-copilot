import time
from contextlib import contextmanager


@contextmanager
def timer():
    state = {"elapsed_ms": 0.0}
    start = time.perf_counter()
    try:
        yield state
    finally:
        state["elapsed_ms"] = (time.perf_counter() - start) * 1000
