"""
Test runner. Works locally and on Gradescope.

Local:     TARGET=../solution python run_tests.py
Gradescope: run_autograder puts the submission on the path and calls this.
"""
import os
import sys
import unittest

# Put the student's code (TARGET) first on the path so `import llm` etc. resolves.
target = os.environ.get("TARGET", "/autograder/submission")
sys.path.insert(0, os.path.abspath(target))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

loader = unittest.TestLoader()
suite = loader.loadTestsFromName("tests_hw3")

try:
    from gradescope_utils.autograder_utils.json_test_runner import JSONTestRunner
    with open("/autograder/results/results.json", "w") as f:
        JSONTestRunner(visibility="visible", stream=f).run(suite)
except Exception:
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
