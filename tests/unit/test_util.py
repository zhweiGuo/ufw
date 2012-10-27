import unittest
import support
import src.util

class UtilTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_example(self):
        '''Test example dummy test'''
        pass

def test_main(): # used by runner.py
    support.run_unittest(
            UtilTestCase
    )

if __name__ == "__main__": # used when standalone
    unittest.main()
