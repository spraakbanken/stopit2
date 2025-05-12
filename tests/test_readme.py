import doctest
import sys
import unittest

from stopit2 import (
    SignalTimeout,
    ThreadingTimeout,
    signal_timeoutable,
    threading_timeoutable,
)

# We run twice the same doctest with two distinct sets of globs
# This one is for testing signals based timeout control
signaling_globs = {"Timeout": SignalTimeout, "timeoutable": signal_timeoutable}

# And this one is for testing threading based timeout control
threading_globs = {"Timeout": ThreadingTimeout, "timeoutable": threading_timeoutable}


def suite():  # Func for setuptools.setup(test_suite=xxx)
    test_suite = unittest.TestSuite()
    if sys.platform in [
        "linux",
        "darwin",
    ]:  # Other OS have no support for signal.SIGALRM
        test_suite.addTest(doctest.DocFileSuite("README.md", globs=signaling_globs))

    test_suite.addTest(doctest.DocFileSuite("README.md", globs=threading_globs))
    return test_suite


def test_all() -> None:
    result = unittest.TextTestRunner(verbosity=2).run(suite())
    assert result.wasSuccessful()


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
