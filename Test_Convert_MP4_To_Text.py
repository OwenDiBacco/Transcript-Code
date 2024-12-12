'''
Not really sure how to implement unit tests in a program like this 
'''

import unittest
import Convert_MP4_To_Text as ct

class TestStringMethods(unittest.TestCase):

    def test_walk_through_directory(self):
        directory = 'C:\\Users\\CMP_OwDiBacco\\Downloads\\Transcript-Code\\Directory-For-Testing'
        output = [{'file_name': '02-Arithmetic Operators', 'file_path': 'C:\\Users\\CMP_OwDiBacco\\Downloads\\Transcript-Code\\Directory-For-Testing\\Txt\\02-Arithmetic Operators'}, {'file_name': '03-Assignment Operators', 'file_path': 'C:\\Users\\CMP_OwDiBacco\\Downloads\\Transcript-Code\\Directory-For-Testing\\Txt\\03-Assignment Operators'}, {'file_name': '04-Comparison Operators', 'file_path': 'C:\\Users\\CMP_OwDiBacco\\Downloads\\Transcript-Code\\Directory-For-Testing\\Txt\\04-Comparison Operators'}, {'file_name': '05-Equality Operators', 'file_path': 'C:\\Users\\CMP_OwDiBacco\\Downloads\\Transcript-Code\\Directory-For-Testing\\Txt\\05-Equality Operators'}, {'file_name': '06-Ternary Operator', 'file_path': 'C:\\Users\\CMP_OwDiBacco\\Downloads\\Transcript-Code\\Directory-For-Testing\\Txt\\06-Ternary Operator'}, {'file_name': '07-Logical Operators', 'file_path': 'C:\\Users\\CMP_OwDiBacco\\Downloads\\Transcript-Code\\Directory-For-Testing\\Txt\\07-Logical Operators'}, {'file_name': '08-Logical Operators with Non-booleans', 'file_path': 'C:\\Users\\CMP_OwDiBacco\\Downloads\\Transcript-Code\\Directory-For-Testing\\Txt\\08-Logical Operators with Non-booleans'}, {'file_name': '09-Bitwise Operators', 'file_path': 'C:\\Users\\CMP_OwDiBacco\\Downloads\\Transcript-Code\\Directory-For-Testing\\Txt\\09-Bitwise Operators'}, {'file_name': '10-Operators Precedence', 'file_path': 'C:\\Users\\CMP_OwDiBacco\\Downloads\\Transcript-Code\\Directory-For-Testing\\Txt\\10-Operators Precedence'}, {'file_name': 'All', 'file_path': 'C:\\Users\\CMP_OwDiBacco\\Downloads\\Transcript-Code\\Directory-For-Testing\\Txt\\All'}, {'file_name': '01-Javascript Operators', 'file_path': 'C:\\Users\\CMP_OwDiBacco\\Downloads\\Transcript-Code\\Directory-For-Testing\\MP4\\01-Javascript Operators'}]
        self.assertEqual(ct.walk_through_directory(directory), output) # directory

    '''
    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
            
    '''

if __name__ == '__main__':
    unittest.main()