# -*- coding: utf-8 -*-
import time
import doctest
import os
import unittest

from stopit import (
    TimeoutException,
    ThreadingTimeout,
    threading_timeoutable,
    SignalTimeout,
    signal_timeoutable,
)

# We run twice the same doctest with two distinct sets of globs
# This one is for testing signals based timeout control
signaling_globs = {"Timeout": SignalTimeout, "timeoutable": signal_timeoutable}

# And this one is for testing threading based timeout control
threading_globs = {"Timeout": ThreadingTimeout, "timeoutable": threading_timeoutable}


class TestNesting(unittest.TestCase):
    handlers = (
        (SignalTimeout,
         ThreadingTimeout,
            )
        if os.name == "posix"
        else (ThreadingTimeout,)
    )

    def aware_wait(self, duration):
        remaining = duration * 100
        while remaining > 0:
            time.sleep(0.01)
            remaining = remaining - 1
        return 0

    def check_nest(self, t1, t2, duration, HandlerClass):
        try:
            with HandlerClass(t1, swallow_exc=False) as to_ctx_mgr1:
                assert to_ctx_mgr1.state == to_ctx_mgr1.EXECUTING
                with HandlerClass(t2, swallow_exc=False) as to_ctx_mgr2:
                    assert to_ctx_mgr2.state == to_ctx_mgr2.EXECUTING
                    self.aware_wait(duration)
                    return "success"
        except TimeoutException:
            if HandlerClass.exception_source is to_ctx_mgr1:
                return "outer"
            elif HandlerClass.exception_source is to_ctx_mgr2:
                return "inner"
            else:
                print(HandlerClass.exception_source)
                return "unknown source"

    def check_nest_swallow(self, t1, t2, duration, HandlerClass):
        with HandlerClass(t1) as to_ctx_mgr1:
            assert to_ctx_mgr1.state == to_ctx_mgr1.EXECUTING
            with HandlerClass(t2) as to_ctx_mgr2:
                assert to_ctx_mgr2.state == to_ctx_mgr2.EXECUTING
                self.aware_wait(duration)
                return "success"
            return "inner"
        return "outer"

    def test_nested_long_inner(self):
        for handler in self.handlers:
            self.assertEqual(self.check_nest(1.0, 10.0, 5.0, handler), "outer")
            self.assertEqual(self.check_nest_swallow(1.0, 10.0, 5.0, handler), "outer")

    def test_nested_success(self):
        for handler in self.handlers:
            start_time = time.time()
            result = self.check_nest_swallow(5.0, 10.0, 1.0, handler)
            duration = time.time() - start_time
            print("   execution took", duration, "for ", handler)
            self.assertEqual(
                result, "success"
            )
            start_time = time.time()
            result = self.check_nest(5.0, 10.0, 1.0, handler)
            duration = time.time() - start_time
            print("   execution took", duration, "for ", handler)
            self.assertEqual(result, "success")

            

    def test_nested_long_outer(self):
        for handler in self.handlers:
            self.assertEqual(self.check_nest(10.0, 1.0, 5.0, handler), "inner")
            self.assertEqual(self.check_nest_swallow(10.0, 1.0, 5.0, handler), "inner")


def suite():  # Func for setuptools.setup(test_suite=xxx)
    test_suite = unittest.TestSuite()
    test_suite.addTest(doctest.DocFileSuite("README.rst", globs=threading_globs))
    if os.name == "posix":  # Other OS have no support for signal.SIGALRM
        test_suite.addTest(doctest.DocFileSuite("README.rst", globs=signaling_globs))
    return test_suite


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
    unittest.main()
