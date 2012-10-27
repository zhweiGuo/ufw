import unittest
import tests.unit.support

class SkeletonTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_example(self):
        '''Test example dummy test'''
        pass

def test_main(): # used by runner.py
    tests.unit.support.run_unittest(
            SkeletonTestCase
    )

if __name__ == "__main__": # used when standalone
    unittest.main()
