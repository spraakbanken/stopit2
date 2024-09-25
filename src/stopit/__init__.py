# -*- coding: utf-8 -*-
"""
======
stopit
======

Public resources from ``stopit``
"""

try:
    from importlib.metadata import version
    __version__ = version(__name__)
except Exception:
    # pkg_resources is deprecated as of Python 3.12 and no longer available for
    # import by default.
    try:
        import pkg_resources
    except Exception:
        LOG.warning(
            "Could not get the package version from importlib or pkg_resources")
        __version__ = 'unknown'
    else:
        __version__ = pkg_resources.get_distribution(__name__).version

from .utils import LOG, TimeoutException
from .threadstop import ThreadingTimeout, async_raise, threading_timeoutable
from .signalstop import SignalTimeout, signal_timeoutable

__all__ = (
    'ThreadingTimeout', 'async_raise', 'threading_timeoutable',
    'SignalTimeout', 'signal_timeoutable'
)
