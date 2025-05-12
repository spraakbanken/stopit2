import time

from stopit2.threadstop import ThreadingTimeout
from stopit2.utils import TimeoutException


def variable_duration_func(duration):
    t0 = time.time()
    while True:
        _dummy = 0
        if time.time() - t0 > duration:
            break


def test_propagating_timeout_exception_thread() -> None:
    result = None
    start_time_ns = time.perf_counter_ns()
    start_time = time.time()
    try:
        with ThreadingTimeout(2.0, swallow_exc=False) as timeout_ctx:
            variable_duration_func(5.0)
    except TimeoutException:
        result = "exception_seen"

    elapsed_ns = time.perf_counter_ns() - start_time_ns
    elapsed = time.time() - start_time
    assert result == "exception_seen"
    assert timeout_ctx.state == timeout_ctx.TIMED_OUT
    assert elapsed < 2.2
    assert elapsed_ns < 2_200_000_000
