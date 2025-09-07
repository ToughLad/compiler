import unittest
from src.thrift_compiler import normalize_type_name, camel_case, Field, thrift_type_str

class TestUtils(unittest.TestCase):

    def test_normalize_type_name(self):
        self.assertIsNone(normalize_type_name(''))
        self.assertEqual(normalize_type_name('String'), 'String')
        self.assertEqual(normalize_type_name('java.util.List'), 'List')
        self.assertEqual(normalize_type_name('List<String>'), 'list<String>')
        self.assertEqual(normalize_type_name('Set<Integer>'), 'set<Integer>')
        self.assertEqual(normalize_type_name('Map<String, Integer>'), 'map<String,Integer>')
        self.assertEqual(normalize_type_name('com.example.Foo'), 'Foo')

    def test_camel_case(self):
        self.assertEqual(camel_case('hello_world'), 'HelloWorld')
        self.assertEqual(camel_case('thrift_idl'), 'ThriftIdl')
        self.assertEqual(camel_case('single_word'), 'SingleWord')

    def test_thrift_type_str(self):
        # Simple types
        field = Field(1, 'test', 'bool')
        self.assertEqual(thrift_type_str(field), 'bool')
        
        field = Field(1, 'test', 'i32', type_name='MyEnum')
        self.assertEqual(thrift_type_str(field), 'MyEnum')
        
        # Struct
        field = Field(1, 'test', 'struct', type_name='MyStruct')
        self.assertEqual(thrift_type_str(field), 'MyStruct')
        
        # List
        field = Field(1, 'test', 'list', val_type='string')
        self.assertEqual(thrift_type_str(field), 'list<string>')
        
        # Set
        field = Field(1, 'test', 'set', val_type='i32')
        self.assertEqual(thrift_type_str(field), 'set<i32>')
        
        # Map
        field = Field(1, 'test', 'map', key_type='string', val_type='i64')
        self.assertEqual(thrift_type_str(field), 'map<string,i64>')

if __name__ == '__main__':
    unittest.main()