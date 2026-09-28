#!/usr/bin/env python3
import argparse
import sys
import unittest

from unit.english_result import EnglishTestRunner


TEST_MODULES = {
    "1": ["unit.test_lexer"],
    "2": ["unit.test_parser"],
    "3": ["unit.test_semantic", "unit.test_codegen_vm"],
    "4": ["unit.test_optimizer"],
    "5": ["unit.test_tail_recursion_optimizer"],
    # Add modules for Assignment 6 and later here.
}


def load_suite(target: str):
    loader = unittest.defaultTestLoader

    if target == "all":
        suite = unittest.TestSuite()
        for modules in TEST_MODULES.values():
            for module in modules:
                suite.addTests(loader.loadTestsFromName(module))
        return suite

    if target not in TEST_MODULES:
        valid = "|".join([*TEST_MODULES.keys(), "all"])
        raise SystemExit(f"usage: ./test [{valid}] [--details]")

    suite = unittest.TestSuite()
    for module in TEST_MODULES[target]:
        suite.addTests(loader.loadTestsFromName(module))
    return suite


def print_details(result):
    for label, failures in (("FAIL", result.failures), ("ERROR", result.errors)):
        for test, traceback_text in failures:
            test_name = test.shortDescription() or test.id()
            print()
            print(f"--- {label}: {test_name} ---")
            print(traceback_text.rstrip())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        choices=[*TEST_MODULES.keys(), "all"],
        help="assignment number to test (default: all)",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="show tracebacks for failed tests",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    suite = load_suite(args.target)

    runner = EnglishTestRunner(verbosity=0)
    result = runner.run(suite)

    if args.details:
        print_details(result)

    total = result.testsRun
    ok = result.pass_count
    ng = result.fail_count

    print()
    print(f"Passed: {ok}")
    print(f"Failed: {ng}")
    print(f"Score: {ok} / {total}")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
