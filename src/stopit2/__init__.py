"""
=======
stopit2
=======

Public resources from ``stopit2``
"""

from .utils import LOG, TimeoutException  # noqa: F401

try:
    from importlib.metadata import version

    __version__ = version(__name__)
except Exception:
    # pkg_resources is deprecated as of Python 3.12 and no longer available for
    # import by default.
    try:
        import pkg_resources
    except Exception:
        LOG.warning("Could not get the package version from importlib or pkg_resources")
        __version__ = "unknown"
    else:
        __version__ = pkg_resources.get_distribution(__name__).version

from .signalstop import SignalTimeout, signal_timeoutable
from .threadstop import ThreadingTimeout, async_raise, threading_timeoutable

__all__ = (
    "ThreadingTimeout",
    "async_raise",
    "threading_timeoutable",
    "SignalTimeout",
    "signal_timeoutable",
    "TimeoutException",
)
