"""
==================
stopit2.signalstop
==================

Control the timeout of blocks or callables with a context manager or a
decorator. Based on the use of signal.SIGALRM
"""

import signal
import typing as t

from .utils import BaseTimeout, TimeoutException, base_timeoutable

ALARMS: list[tuple[t.Any, int]] = []


def handle_alarms(signum, frame):
    global ALARMS
    new_alarms = [
        (
            ctx,
            max(0, remaining - 1),
        )
        for ctx, remaining in ALARMS
    ]
    expired = [ctx for ctx, remaining in new_alarms if remaining == 0]
    ALARMS = [
        (
            ctx,
            remaining,
        )
        for ctx, remaining in new_alarms
        if remaining > 0
    ]
    if ALARMS:
        signal.alarm(1)
    for task in expired:
        task.stop()
        break


class SignalTimeout(BaseTimeout):
    """Context manager for limiting in the time the execution of a block
    using signal.SIGALRM Unix signal.

    See :class:`stopit.utils.BaseTimeout` for more information
    """

    def __init__(self, seconds, swallow_exc=True):
        seconds = int(seconds)  # alarm delay for signal MUST be int
        super(SignalTimeout, self).__init__(seconds, swallow_exc)

    def stop(self):
        self.state = BaseTimeout.TIMED_OUT
        self.__class__.exception_source = self
        raise TimeoutException(
            "Block exceeded maximum timeout value (%d seconds)." % self.seconds
        )

    # Required overrides
    def setup_interrupt(self):
        global ALARMS
        for ctx, remaining in ALARMS:
            if ctx is self:
                return
        if len(ALARMS) == 0:
            signal.signal(signal.SIGALRM, handle_alarms)
            signal.alarm(1)
        ALARMS.append(
            (
                self,
                int(self.seconds),
            )
        )

    def suppress_interrupt(self):
        global ALARMS
        ALARMS = [(ctx, remaining) for ctx, remaining in ALARMS if ctx is not self]
        if len(ALARMS) == 0:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, signal.SIG_DFL)


class signal_timeoutable(base_timeoutable):  # noqa
    """A function or method decorator that raises a ``TimeoutException`` to
    decorated functions that should not last a certain amount of time.
    this one uses ``SignalTimeout`` context manager.

    See :class:`.utils.base_timoutable`` class for further comments.
    """

    to_ctx_mgr = SignalTimeout  # type: ignore [assignment]
