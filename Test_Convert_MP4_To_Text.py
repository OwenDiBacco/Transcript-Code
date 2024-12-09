'''
Not really sure how to implement unit tests in a program like this 
'''

import unittest
import Convert_MP4_To_Text as ct

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual(ct.create_threads_for_mp4_folder(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()