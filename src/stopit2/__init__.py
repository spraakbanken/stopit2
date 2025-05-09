# -*- coding: utf-8 -*-
"""
======
stopit
======

Public resources from ``stopit``
"""

import pkg_resources

from .signalstop import SignalTimeout, signal_timeoutable
from .threadstop import ThreadingTimeout, async_raise, threading_timeoutable
from .utils import LOG, TimeoutException

# PEP 396 style version marker
try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    LOG.warning("Could not get the package version from pkg_resources")
    __version__ = "unknown"

__all__ = (
    "ThreadingTimeout",
    "async_raise",
    "threading_timeoutable",
    "SignalTimeout",
    "signal_timeoutable",
)
