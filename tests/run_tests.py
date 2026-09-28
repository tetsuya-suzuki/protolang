#!/usr/bin/env python3
import argparse
import os
import sys
import unittest


class CompactTestResult(unittest.TestResult):
    """Print one compact result line for each test."""

    def __init__(self, *, show_details: bool = False) -> None:
        super().__init__()
        self.show_details = show_details
        self.pass_count = 0
        self.fail_count = 0

    @staticmethod
    def _test_name(test: unittest.TestCase) -> str:
        return test.shortDescription() or test.id()

    def addSuccess(self, test: unittest.TestCase) -> None:
        super().addSuccess(test)
        self.pass_count += 1
        print(f"[PASS] {self._test_name(test)}")

    def addFailure(self, test: unittest.TestCase, err) -> None:
        super().addFailure(test, err)
        self.fail_count += 1
        print(f"[FAIL] {self._test_name(test)}")

    def addError(self, test: unittest.TestCase, err) -> None:
        super().addError(test, err)
        self.fail_count += 1
        print(f"[FAIL] {self._test_name(test)}")

    def addUnexpectedSuccess(self, test: unittest.TestCase) -> None:
        super().addUnexpectedSuccess(test)
        self.fail_count += 1
        print(f"[FAIL] {self._test_name(test)} (unexpected success)")

    def addSkip(self, test: unittest.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        print(f"[SKIP] {self._test_name(test)}: {reason}")

    def addExpectedFailure(self, test: unittest.TestCase, err) -> None:
        super().addExpectedFailure(test, err)
        print(f"[XFAIL] {self._test_name(test)}")


def load_suite() -> unittest.TestSuite:
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)
    return unittest.defaultTestLoader.discover("tests", pattern="test_*.py")


def print_details(result: CompactTestResult) -> None:
    if not result.show_details:
        return

    for label, failures in (("FAIL", result.failures), ("ERROR", result.errors)):
        for test, traceback_text in failures:
            print()
            print(f"--- {label}: {result._test_name(test)} ---")
            print(traceback_text.rstrip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--details",
        action="store_true",
        help="show tracebacks for failed tests",
    )
    args = parser.parse_args()

    result = CompactTestResult(show_details=args.details)
    load_suite().run(result)

    print_details(result)

    print()
    print(f"Passed: {result.pass_count}")
    print(f"Failed: {result.fail_count}")
    print(f"Total:  {result.testsRun}")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
