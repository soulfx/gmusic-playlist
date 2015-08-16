# Author: Sam Garrett <samdgarrett@gmail.com>
# License: MIT <LICENSE>

import unittest
from common import *

class TestCommon(unittest.TestCase):
  
    def test_quote_unquote(self):
        """ test for verifying the quoting and unquoting that occurs in track values """
        test_values = (("", ""),
                       ("bog", "bog"),
                       ("\"bog", "\"\"\"bog\""),
                       ("\"bog\"", "\"\"\"bog\"\"\""),
                       ("b\"o\"g", "\"b\"\"o\"\"g\""),
                       ("\"", "\"\"\"\""))
        for (invalue, expected) in test_values:
            actual_out = handle_quote_output(invalue)
            self.assertEqual(actual_out, expected) 

            actual_in = handle_quote_input(actual_out)
            self.assertEqual(actual_in, invalue) 

if __name__ == '__main__':
  unittest.main()
