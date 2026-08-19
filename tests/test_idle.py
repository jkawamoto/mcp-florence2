#  test_idle.py
#
#  Copyright (c) 2025-2026 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
import threading
import time

from mcp_florence2.idle import IdleProxy, IdleReleased


class Counter:
    """Stands in for a model: records how often it was built and answers calls."""

    builds = 0

    def __init__(self) -> None:
        type(self).builds += 1

    def double(self, value: int) -> int:
        return value * 2


def test_builds_lazily() -> None:
    Counter.builds = 0
    cache = IdleReleased(Counter, timeout=60, name="counter")

    assert Counter.builds == 0

    cache.get()
    assert Counter.builds == 1


def test_reuses_while_active() -> None:
    Counter.builds = 0
    cache = IdleReleased(Counter, timeout=60, name="counter")

    first = cache.get()
    second = cache.get()

    assert first is second
    assert Counter.builds == 1


def test_releases_after_timeout() -> None:
    Counter.builds = 0
    cache = IdleReleased(Counter, timeout=0.1, name="counter")

    cache.get()
    time.sleep(0.4)

    # The next call has to build a second instance, proving the first was dropped.
    cache.get()
    assert Counter.builds == 2


def test_use_postpones_the_release() -> None:
    Counter.builds = 0
    cache = IdleReleased(Counter, timeout=0.3, name="counter")

    first = cache.get()
    for _ in range(4):
        time.sleep(0.1)
        # Each call restarts the countdown, so the object should survive well past
        # the timeout as long as requests keep arriving.
        assert cache.get() is first

    assert Counter.builds == 1


def test_zero_timeout_never_releases() -> None:
    Counter.builds = 0
    cache = IdleReleased(Counter, timeout=0, name="counter")

    cache.get()
    time.sleep(0.3)
    cache.get()

    assert Counter.builds == 1


def test_release_is_safe_when_nothing_is_loaded() -> None:
    Counter.builds = 0
    cache = IdleReleased(Counter, timeout=60, name="counter")

    cache.release()
    cache.release()

    assert Counter.builds == 0


def test_proxy_forwards_calls_and_reloads() -> None:
    Counter.builds = 0
    proxy = IdleProxy(IdleReleased(Counter, timeout=0.1, name="counter"))

    assert proxy.double(21) == 42
    assert Counter.builds == 1

    time.sleep(0.4)

    # Released in the meantime, but the proxy rebuilds transparently.
    assert proxy.double(4) == 8
    assert Counter.builds == 2


def test_concurrent_use_builds_once() -> None:
    Counter.builds = 0
    cache = IdleReleased(Counter, timeout=60, name="counter")
    seen: list[object] = []
    barrier = threading.Barrier(8)

    def worker() -> None:
        barrier.wait()
        seen.append(cache.get())

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert Counter.builds == 1
    assert all(item is seen[0] for item in seen)
