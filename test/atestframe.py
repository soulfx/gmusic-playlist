# put the parent directory onto the path
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import unittest

def run_test():
    unittest.main(verbosity=2)
