"""
==================
stopit2.threadstop
==================

Raise asynchronous exceptions in other thread, control the timeout of blocks
or callables with a context manager or a decorator.
"""

import ctypes
import sys
import threading

from .utils import BaseTimeout, TimeoutException, base_timeoutable

if sys.version_info < (3, 7):
    tid_ctype = ctypes.c_long
else:
    tid_ctype = ctypes.c_ulong


def async_raise(target_tid, exception):
    """Raises an asynchronous exception in another thread.
    Read http://docs.python.org/c-api/init.html#PyThreadState_SetAsyncExc
    for further enlightenments.

    :param target_tid: target thread identifier
    :param exception: Exception class to be raised in that thread
    """
    # Ensuring and releasing GIL are useless since we're not in C
    # gil_state = ctypes.pythonapi.PyGILState_Ensure()
    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        tid_ctype(target_tid), ctypes.py_object(exception)
    )
    # ctypes.pythonapi.PyGILState_Release(gil_state)
    if ret == 0:
        raise ValueError("Invalid thread ID {}".format(target_tid))
    elif ret > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid_ctype(target_tid), None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class ThreadingTimeout(BaseTimeout):
    """Context manager for limiting in the time the execution of a block
    using asynchronous threads launching exception.

    See :class:`stopit.utils.BaseTimeout` for more information
    """

    # This class property keep track about who produced the
    # exception.

    def __init__(self, seconds, swallow_exc=True):
        # Ensure that any new handler find a clear
        # pointer
        super(ThreadingTimeout, self).__init__(seconds, swallow_exc)
        self.target_tid = threading.current_thread().ident
        self.timer = None  # PEP8

    def stop(self):
        """Called by timer thread at timeout. Raises a Timeout exception in the
        caller thread
        """
        self.state = BaseTimeout.TIMED_OUT
        self.__class__.exception_source = self
        async_raise(self.target_tid, TimeoutException)

    # Required overrides
    def setup_interrupt(self):
        """Setting up the resource that interrupts the block"""
        self.timer = threading.Timer(self.seconds, self.stop)
        self.timer.start()

    def suppress_interrupt(self):
        """Removing the resource that interrupts the block"""
        self.timer.cancel()


class threading_timeoutable(base_timeoutable):  # noqa
    """A function or method decorator that raises a ``TimeoutException`` to
    decorated functions that should not last a certain amount of time.
    this one uses ``ThreadingTimeout`` context manager.

    See :class:`.utils.base_timoutable`` class for further comments.
    """

    to_ctx_mgr = ThreadingTimeout  # type: ignore [assignment]
