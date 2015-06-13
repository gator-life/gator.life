import unittest
from server.dummyfortest import DummyForTest


class DummyForTestTests(unittest.TestCase):

    def test_hello_world(self):
        x = DummyForTest()
        self.assertEquals('hello world', x.hello_world())

if __name__ == '__main__':
    unittest.main()