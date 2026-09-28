import io
import unittest


class EnglishTestResult(unittest.TextTestResult):
    """A unittest result class that prints test results as [PASS]/[FAIL]."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pass_count = 0
        self.fail_count = 0

    def _test_name(self, test):
        return test.shortDescription() or test.id()

    def addSuccess(self, test):
        super().addSuccess(test)
        self.pass_count += 1
        print(f"[PASS] {self._test_name(test)}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.fail_count += 1
        print(f"[FAIL] {self._test_name(test)}")

    def addError(self, test, err):
        super().addError(test, err)
        self.fail_count += 1
        print(f"[FAIL] {self._test_name(test)}")


class EnglishTestRunner(unittest.TextTestRunner):
    """A unittest runner that uses EnglishTestResult."""

    resultclass = EnglishTestResult

    def __init__(self, *args, **kwargs):
        kwargs["stream"] = io.StringIO()
        super().__init__(*args, **kwargs)
