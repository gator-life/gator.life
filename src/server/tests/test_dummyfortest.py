import unittest
from server.dummyfortest import DummyForTest

class DummyForTestTests(unittest.TestCase):

    def test_hello_world(self):
        my_class = DummyForTest()
        self.assertEquals('hello world', my_class.hello_world())

if __name__ == '__main__':
    unittest.main()
