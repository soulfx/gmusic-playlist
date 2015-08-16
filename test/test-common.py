from atestframe import *
from common import *

class TestCommon(unittest.TestCase):

    def test_get_csv_fields(self):
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
        self.assertEqual(handle_quote_input(u''),u'')
        self.assertEqual(handle_quote_input(u'a'),u'a')
        self.assertEqual(handle_quote_input(u'""'),u'')
        self.assertEqual(handle_quote_input(u'""asdf""'),u'"asdf"')
        self.assertEqual(handle_quote_input(u'"asdf"'),u'asdf')

run_test()
