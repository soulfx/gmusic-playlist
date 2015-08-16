from atestframe import *
from common import *

class TestCommon(unittest.TestCase):

    def test_get_csv_fields(self):
        """ test that quoted and unquoted fields are being recognized """
        fields = get_csv_fields(u'something,"good",to "eat","like a ""hot""",dog',u',')
        self.assertEqual(fields[0],u'something')
        self.assertEqual(fields[1],u'good')
        self.assertEqual(fields[2],u'to "eat"')
        self.assertEqual(fields[3],u'like a "hot"')
        self.assertEqual(fields[4],u'dog')
        fields = get_csv_fields(u',hello',u',')
        self.assertEqual(fields[0],u'')
        self.assertEqual(fields[1],u'hello')
        fields = get_csv_fields(u'test,"commas, in, the, field"',u',')
        self.assertEqual(len(fields),2)
        self.assertEqual(fields[0],u'test')
        self.assertEqual(fields[1],u'commas, in, the, field')

    def test_handle_quote_input(self):
        """ test that quotes are being removed as expected """
        self.assertEqual(handle_quote_input(u''),u'')
        self.assertEqual(handle_quote_input(u'a'),u'a')
        self.assertEqual(handle_quote_input(u'""'),u'')
        self.assertEqual(handle_quote_input(u'""asdf""'),u'"asdf"')
        self.assertEqual(handle_quote_input(u'"asdf"'),u'asdf')

    def test_handle_quote_output(self):
        """ test that quotes are applied only when needed """
        self.assertEqual(handle_quote_output("nothing to quote"),"nothing to quote")
        self.assertEqual(handle_quote_output('this "needs" quoting'),'"this ""needs"" quoting"')
        self.assertEqual(handle_quote_output('tsep, in field'),'"tsep, in field"')

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

run_test()
