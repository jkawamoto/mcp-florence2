#  subprocess.py
#
#  Copyright (c) 2025 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php

from __future__ import annotations

from contextlib import closing
from functools import wraps
from multiprocessing import Process, SimpleQueue
from typing import Any, Callable, Generic, TypeVar, ParamSpec

import dill

T = TypeVar("T")
P = ParamSpec("P")


class Target(Generic[T, P]):
    f: Callable[P, T]
    queue: SimpleQueue[T]

    def __init__(self, f: Callable[P, T], queue: SimpleQueue[T]) -> None:
        self.f = f
        self.queue = queue

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        self.queue.put(self.f(*args, **kwargs))

    def __getstate__(self) -> dict[str, Any]:
        state = self.__dict__.copy()
        state["f"] = dill.dumps(self.f)

        return state

    def __setstate__(self, state: dict[str, Any]) -> None:
        state["f"] = dill.loads(state["f"])
        self.__dict__.update(state)


def subprocess(f: Callable[P, T]) -> Callable[P, T]:
    """Wraps a function to execute it in a subprocess.

    The target function will be run
    within a separate process, and its return value will be retrieved and returned
    to the caller.

    Wrapped functions maintain their original names and docstrings due to the
    `@wraps` decorator.

    Args:
        f: The function to be executed in a subprocess. It must be serializable to be passed to a separate process.
    Returns:
        A new function equivalent to `f`, but executed in a separate process when called.
    """

    @wraps(f)
    def _(*args: P.args, **kwargs: P.kwargs) -> T:
        queue: SimpleQueue[T] = SimpleQueue()
        with closing(queue) as queue:
            with closing(Process(target=Target(f, queue), args=args, kwargs=kwargs)) as proc:
                proc.start()
                proc.join()
            return queue.get()

    return _
