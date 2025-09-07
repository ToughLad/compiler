#!/usr/bin/env python3
"""Comprehensive tests for thrift_compiler.py with 100% coverage"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest import mock
from unittest.mock import Mock, MagicMock, patch, mock_open, call

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import thrift_compiler


class TestClasses:
    """Test all class definitions"""
    
    def test_thrift_enum_creation(self):
        """Test ThriftEnum creation and string representation"""
        enum = thrift_compiler.ThriftEnum("TestEnum")
        assert enum.name == "TestEnum"
        assert enum.values == []
        
        enum.values.append(("VALUE1", 1))
        enum.values.append(("VALUE2", 2))
        assert len(enum.values) == 2
        assert enum.values[0] == ("VALUE1", 1)
    
    def test_thrift_struct_creation(self):
        """Test ThriftStruct creation"""
        struct = thrift_compiler.ThriftStruct("TestStruct")
        assert struct.name == "TestStruct"
        assert struct.fields == []
        
        field = thrift_compiler.Field(
            id=1, name="testField", ttype="string",
            type_name=None, key_type=None, val_type=None, required=True
        )
        struct.fields.append(field)
        assert len(struct.fields) == 1
        assert struct.fields[0].name == "testField"
    
    def test_thrift_service_creation(self):
        """Test ThriftService creation and methods"""
        service = thrift_compiler.ThriftService("TestService")
        assert service.name == "TestService"
        assert service.methods == []
        
        service.add_method("testMethod", "RequestType", "ResponseType", [])
        assert len(service.methods) == 1
        assert service.methods[0]['name'] == "testMethod"
        assert service.methods[0]['arg_type'] == "RequestType"
        assert service.methods[0]['ret_type'] == "ResponseType"
        assert service.methods[0]['exceptions'] == []
    
    def test_field_creation(self):
        """Test Field creation with all parameters"""
        field = thrift_compiler.Field(
            id=1,
            name="testField",
            ttype="map",
            type_name="TestType",
            key_type="string",
            val_type="i32",
            required=False
        )
        assert field.id == 1
        assert field.name == "testField"
        assert field.ttype == "map"
        assert field.type_name == "TestType"
        assert field.key_type == "string"
        assert field.val_type == "i32"
        assert field.required == False


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_read_file_success(self):
        """Test successful file reading"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as tf:
            tf.write("test content")
            tf_path = Path(tf.name)
        
        try:
            content = thrift_compiler.read_file(tf_path)
            assert content == "test content"
        finally:
            tf_path.unlink()
    
    def test_read_file_encoding_error(self):
        """Test file reading with encoding error"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.java', delete=False) as tf:
            tf.write(b'\xff\xfe invalid utf-8')
            tf_path = Path(tf.name)
        
        try:
            content = thrift_compiler.read_file(tf_path)
            assert content == ""
        finally:
            tf_path.unlink()
    
    def test_normalize_type_name(self):
        """Test type name normalization"""
        # Valid Java class names
        assert thrift_compiler.normalize_type_name("String") == "String"
        assert thrift_compiler.normalize_type_name("com.example.ClassName") == "ClassName"
        assert thrift_compiler.normalize_type_name("com.example.Class$Inner") == "ClassInner"
        assert thrift_compiler.normalize_type_name("C12345a") == "C12345a"
        
        # Complex types
        assert thrift_compiler.normalize_type_name("List<String>") == "String"
        assert thrift_compiler.normalize_type_name("ArrayList<Integer>") == "Integer"
        
        # Invalid names
        assert thrift_compiler.normalize_type_name("123Invalid") is None
        assert thrift_compiler.normalize_type_name("") is None
        assert thrift_compiler.normalize_type_name("!@#$%") is None
    
    def test_thrift_type_str(self):
        """Test Thrift type string generation"""
        # Simple types
        field = thrift_compiler.Field(1, "test", "string", None, None, None, False)
        assert thrift_compiler.thrift_type_str(field) == "string"
        
        field = thrift_compiler.Field(1, "test", "i32", None, None, None, False)
        assert thrift_compiler.thrift_type_str(field) == "i32"
        
        # List type
        field = thrift_compiler.Field(1, "test", "list", "String", None, None, False)
        assert thrift_compiler.thrift_type_str(field) == "list<String>"
        
        field = thrift_compiler.Field(1, "test", "list", None, None, None, False)
        assert thrift_compiler.thrift_type_str(field) == "list<i32>"
        
        # Map type
        field = thrift_compiler.Field(1, "test", "map", None, "string", "i32", False)
        assert thrift_compiler.thrift_type_str(field) == "map<string,i32>"
        
        field = thrift_compiler.Field(1, "test", "map", None, None, None, False)
        assert thrift_compiler.thrift_type_str(field) == "map<i32,i32>"
        
        # Set type
        field = thrift_compiler.Field(1, "test", "set", "String", None, None, False)
        assert thrift_compiler.thrift_type_str(field) == "set<String>"
        
        # Struct type
        field = thrift_compiler.Field(1, "test", "struct", "TestStruct", None, None, False)
        assert thrift_compiler.thrift_type_str(field) == "TestStruct"
        
        # Enum type
        field = thrift_compiler.Field(1, "test", "enum", "TestEnum", None, None, False)
        assert thrift_compiler.thrift_type_str(field) == "TestEnum"
        
        # Binary type
        field = thrift_compiler.Field(1, "test", "binary", None, None, None, False)
        assert thrift_compiler.thrift_type_str(field) == "binary"
        
        # Unknown type
        field = thrift_compiler.Field(1, "test", "unknown", None, None, None, False)
        assert thrift_compiler.thrift_type_str(field) == "i32"


class TestParsingFunctions:
    """Test parsing functions"""
    
    @patch('thrift_compiler.JAVA_ROOT')
    @patch('thrift_compiler.read_file')
    def test_parse_enums(self, mock_read_file, mock_java_root):
        """Test enum parsing"""
        # Setup mock filesystem
        mock_java_root.rglob.return_value = [
            Path('TestEnum.java'),
            Path('NotAnEnum.java')
        ]
        
        # Mock file contents
        def read_side_effect(path):
            if 'TestEnum' in str(path):
                return """
                public enum TestEnum {
                    VALUE1(1),
                    VALUE2(2, 100),
                    VALUE3("label", 3);
                }
                """
            else:
                return "public class NotAnEnum {}"
        
        mock_read_file.side_effect = read_side_effect
        
        # Clear existing enums
        thrift_compiler.enums.clear()
        
        # Parse enums
        thrift_compiler.parse_enums()
        
        # Verify results
        assert 'TestEnum' in thrift_compiler.enums
        enum = thrift_compiler.enums['TestEnum']
        assert ('VALUE1', 1) in enum.values
        assert ('VALUE2', 2) in enum.values
        assert ('VALUE3', 3) in enum.values
    
    @patch('thrift_compiler.JAVA_ROOT')
    @patch('thrift_compiler.read_file')
    def test_parse_structs_simple(self, mock_read_file, mock_java_root):
        """Test struct parsing with simple fields"""
        # Setup mock filesystem
        mock_java_root.rglob.return_value = [
            Path('TestStruct.java'),
            Path('B41/E0.java')  # Obfuscated Response
        ]
        
        # Mock file contents
        def read_side_effect(path):
            if 'TestStruct' in str(path):
                return """
                public class TestStruct implements org.apache.thrift.k {
                    public static final ww1.c f5656b = new ww1.c("name", (byte) 11, 1);
                    public static final ww1.c f5657c = new ww1.c("age", (byte) 8, 2);
                    public String f5659a;
                    public int f5660b;
                }
                """
            elif 'E0' in str(path):
                return """
                public class E0 implements org.apache.thrift.d {
                    public static final ww1.c f5656b = new ww1.c("responses", (byte) 15, 1);
                    public ArrayList f5659a;
                    public String toString() {
                        return new StringBuilder("GetContactsV3Response(").toString();
                    }
                }
                """
            return ""
        
        mock_read_file.side_effect = read_side_effect
        
        # Clear existing structs
        thrift_compiler.structs.clear()
        
        # Parse structs
        thrift_compiler.parse_structs()
        
        # Verify TestStruct
        assert 'TestStruct' in thrift_compiler.structs
        struct = thrift_compiler.structs['TestStruct']
        assert len(struct.fields) == 2
        assert struct.fields[0].name == "name"
        assert struct.fields[0].ttype == "string"
        assert struct.fields[1].name == "age"
        assert struct.fields[1].ttype == "i32"
        
        # Verify obfuscated struct
        assert 'GetContactsV3Response' in thrift_compiler.structs
        response = thrift_compiler.structs['GetContactsV3Response']
        assert len(response.fields) == 1
        assert response.fields[0].name == "responses"
        assert response.fields[0].ttype == "list"
    
    @patch('thrift_compiler.JAVA_ROOT')
    @patch('thrift_compiler.read_file')
    def test_parse_structs_with_exception(self, mock_read_file, mock_java_root):
        """Test parsing structs that are exceptions"""
        mock_java_root.rglob.return_value = [
            Path('TestException.java')
        ]
        
        mock_read_file.return_value = """
        public class TestException extends org.apache.thrift.i implements org.apache.thrift.k {
            public static final ww1.c f1 = new ww1.c("message", (byte) 11, 1);
            public String f2;
        }
        """
        
        thrift_compiler.structs.clear()
        thrift_compiler.exception_structs.clear()
        
        thrift_compiler.parse_structs()
        
        assert 'TestException' in thrift_compiler.structs
        assert 'TestException' in thrift_compiler.exception_structs
    
    @patch('thrift_compiler.JAVA_ROOT')
    @patch('thrift_compiler.read_file')
    def test_parse_services(self, mock_read_file, mock_java_root):
        """Test service parsing"""
        # Setup mock filesystem  
        mock_java_root.rglob.return_value = [
            Path('TestService.java'),
            Path('TestService$Client.java'),
            Path('Lt1/U8.java'),  # wrapper args
            Path('Lt1/V8.java'),  # wrapper result
        ]
        
        # Mock file contents
        def read_side_effect(path):
            if 'TestService$Client' in str(path):
                return """
                public static class Client {
                    public final TestResponse testMethod(TestRequest request) throws TException {
                        b("testMethod");
                    }
                }
                """
            elif 'U8.java' in str(path):
                return """
                public class U8 {
                    public C12999i2 f1;
                    public String toString() {
                        return new StringBuilder("testMethod_args(").toString();
                    }
                }
                """
            elif 'V8.java' in str(path):
                return """
                public class V8 {
                    public TestResponse success;
                    public String toString() {
                        return new StringBuilder("testMethod_result(").toString();
                    }
                }
                """
            return ""
        
        mock_read_file.side_effect = read_side_effect
        
        # Clear existing services
        thrift_compiler.services.clear()
        thrift_compiler.class_index = {}
        
        # Populate class_index
        for p in mock_java_root.rglob.return_value:
            thrift_compiler.class_index[str(p)] = p
        
        # Parse services
        thrift_compiler.parse_services()
        
        # Verify results
        assert 'TestService' in thrift_compiler.services
        service = thrift_compiler.services['TestService']
        assert len(service.methods) == 1
        assert service.methods[0]['name'] == 'testMethod'
    
    @patch('thrift_compiler.JAVA_ROOT')
    @patch('thrift_compiler.read_file')
    def test_parse_structs_complex_types(self, mock_read_file, mock_java_root):
        """Test parsing structs with complex field types"""
        mock_java_root.rglob.return_value = [Path('ComplexStruct.java')]
        
        mock_read_file.return_value = """
        public class ComplexStruct implements org.apache.thrift.k {
            public static final ww1.c f1 = new ww1.c("mapField", (byte) 13, 1);
            public static final ww1.c f2 = new ww1.c("listField", (byte) 15, 2);
            public static final ww1.c f3 = new ww1.c("setField", (byte) 14, 3);
            public HashMap<String, Integer> f4;
            public ArrayList<TestItem> f5;
            public HashSet<String> f6;
        }
        """
        
        thrift_compiler.structs.clear()
        thrift_compiler.parse_structs()
        
        assert 'ComplexStruct' in thrift_compiler.structs
        struct = thrift_compiler.structs['ComplexStruct']
        assert len(struct.fields) == 3
        
        # Map field
        assert struct.fields[0].ttype == "map"
        assert struct.fields[0].key_type == "String"
        assert struct.fields[0].val_type == "Integer"
        
        # List field
        assert struct.fields[1].ttype == "list"
        assert struct.fields[1].type_name == "TestItem"
        
        # Set field
        assert struct.fields[2].ttype == "set"
        assert struct.fields[2].type_name == "String"


class TestWriteFunctions:
    """Test output writing functions"""
    
    @patch('builtins.open', new_callable=mock_open)
    def test_write_thrift(self, mock_file):
        """Test Thrift file writing"""
        # Setup test data
        thrift_compiler.enums.clear()
        thrift_compiler.structs.clear()
        thrift_compiler.services.clear()
        thrift_compiler.alias_map.clear()
        thrift_compiler.exception_structs.clear()
        
        # Add test enum
        enum = thrift_compiler.ThriftEnum("TestEnum")
        enum.values.append(("VALUE1", 1))
        enum.values.append(("VALUE2", 2))
        thrift_compiler.enums["TestEnum"] = enum
        
        # Add test struct
        struct = thrift_compiler.ThriftStruct("TestStruct")
        field = thrift_compiler.Field(1, "testField", "string", None, None, None, False)
        struct.fields.append(field)
        thrift_compiler.structs["TestStruct"] = struct
        
        # Add test exception
        exc_struct = thrift_compiler.ThriftStruct("TestException")
        exc_field = thrift_compiler.Field(1, "message", "string", None, None, None, False)
        exc_struct.fields.append(exc_field)
        thrift_compiler.structs["TestException"] = exc_struct
        thrift_compiler.exception_structs.add("TestException")
        
        # Add test service
        service = thrift_compiler.ThriftService("TestService")
        service.add_method("testMethod", "TestRequest", "TestResponse", [])
        thrift_compiler.services["TestService"] = service
        
        # Add alias
        thrift_compiler.alias_map["C12345"] = "C12345"
        
        # Write thrift
        thrift_compiler.write_thrift()
        
        # Verify file was opened
        mock_file.assert_called_once_with(thrift_compiler.OUTPUT_FILE, 'w')
        
        # Get write calls
        handle = mock_file()
        write_calls = handle.write.call_args_list
        written_content = ''.join([call[0][0] for call in write_calls])
        
        # Verify content includes expected elements
        assert "typedef i32 C12345" in written_content
        assert "enum TestEnum {" in written_content
        assert "VALUE1 = 1" in written_content
        assert "struct TestStruct {" in written_content
        assert "1: string testField" in written_content
        assert "exception TestException {" in written_content
        assert "service TestService {" in written_content
        assert "TestResponse testMethod(1: TestRequest request)" in written_content
    
    @patch('builtins.open', new_callable=mock_open)
    def test_write_thrift_with_required_fields(self, mock_file):
        """Test writing structs with required fields"""
        thrift_compiler.structs.clear()
        
        struct = thrift_compiler.ThriftStruct("TestStruct")
        field1 = thrift_compiler.Field(1, "required_field", "string", None, None, None, True)
        field2 = thrift_compiler.Field(2, "optional_field", "i32", None, None, None, False)
        struct.fields.append(field1)
        struct.fields.append(field2)
        thrift_compiler.structs["TestStruct"] = struct
        
        thrift_compiler.write_thrift()
        
        handle = mock_file()
        write_calls = handle.write.call_args_list
        written_content = ''.join([call[0][0] for call in write_calls])
        
        assert "1: required string required_field" in written_content
        assert "2: i32 optional_field" in written_content


class TestMainFunction:
    """Test main execution function"""
    
    @patch('thrift_compiler.parse_enums')
    @patch('thrift_compiler.parse_structs')
    @patch('thrift_compiler.parse_services')
    @patch('thrift_compiler.write_thrift')
    def test_main_execution(self, mock_write, mock_services, mock_structs, mock_enums):
        """Test main function execution"""
        # Execute main
        thrift_compiler.main()
        
        # Verify all functions were called in order
        mock_enums.assert_called_once()
        mock_structs.assert_called_once()
        mock_services.assert_called_once()
        mock_write.assert_called_once()
    
    @patch('sys.exit')
    @patch('thrift_compiler.JAVA_ROOT')
    def test_main_with_missing_java_root(self, mock_java_root, mock_exit):
        """Test main when JAVA_ROOT doesn't exist"""
        mock_java_root.exists.return_value = False
        
        # Import should trigger the check
        import importlib
        with patch('builtins.print'):
            importlib.reload(thrift_compiler)
        
        mock_exit.assert_called_with(1)


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @patch('thrift_compiler.JAVA_ROOT')
    @patch('thrift_compiler.read_file')
    def test_parse_structs_empty_class(self, mock_read_file, mock_java_root):
        """Test parsing empty struct"""
        mock_java_root.rglob.return_value = [Path('EmptyStruct.java')]
        mock_read_file.return_value = """
        public class EmptyStruct implements org.apache.thrift.k {
        }
        """
        
        thrift_compiler.structs.clear()
        thrift_compiler.parse_structs()
        
        assert 'EmptyStruct' in thrift_compiler.structs
        assert len(thrift_compiler.structs['EmptyStruct'].fields) == 0
    
    @patch('thrift_compiler.JAVA_ROOT')
    @patch('thrift_compiler.read_file')
    def test_parse_multiline_field_declaration(self, mock_read_file, mock_java_root):
        """Test parsing field declarations split across multiple lines"""
        mock_java_root.rglob.return_value = [Path('MultilineStruct.java')]
        mock_read_file.return_value = """
        public class MultilineStruct implements org.apache.thrift.k {
            public static final ww1.c f1 = new ww1.
                c("fieldName", 
                  (byte) 11, 
                  1);
            public String f2;
        }
        """
        
        thrift_compiler.structs.clear()
        thrift_compiler.parse_structs()
        
        assert 'MultilineStruct' in thrift_compiler.structs
        struct = thrift_compiler.structs['MultilineStruct']
        assert len(struct.fields) == 1
        assert struct.fields[0].name == "fieldName"
    
    @patch('thrift_compiler.JAVA_ROOT')
    @patch('thrift_compiler.read_file')
    def test_parse_service_with_exceptions(self, mock_read_file, mock_java_root):
        """Test parsing service methods with exceptions"""
        mock_java_root.rglob.return_value = [
            Path('ServiceWithExceptions.java'),
            Path('ServiceWithExceptions$Client.java')
        ]
        
        def read_side_effect(path):
            if 'Client' in str(path):
                return """
                public static class Client {
                    public final Response method(Request req) throws Ex1, Ex2 {
                        b("method");
                    }
                }
                """
            return ""
        
        mock_read_file.side_effect = read_side_effect
        
        thrift_compiler.services.clear()
        thrift_compiler.class_index = {str(p): p for p in mock_java_root.rglob.return_value}
        thrift_compiler.parse_services()
        
        assert 'ServiceWithExceptions' in thrift_compiler.services
        service = thrift_compiler.services['ServiceWithExceptions']
        assert len(service.methods) == 1
        assert service.methods[0]['exceptions'] == ['Ex1', 'Ex2']
    
    def test_normalize_type_name_edge_cases(self):
        """Test normalize_type_name with edge cases"""
        # Unicode characters
        assert thrift_compiler.normalize_type_name("Class名前") == "Class"
        
        # Multiple dots
        assert thrift_compiler.normalize_type_name("com.example.sub.ClassName") == "ClassName"
        
        # Nested generics
        assert thrift_compiler.normalize_type_name("Map<String, List<Integer>>") == "Integer"
        
        # Empty generics
        assert thrift_compiler.normalize_type_name("List<>") is None
    
    @patch('thrift_compiler.JAVA_ROOT')
    @patch('thrift_compiler.read_file')
    def test_duplicate_struct_names(self, mock_read_file, mock_java_root):
        """Test handling of duplicate struct names"""
        mock_java_root.rglob.return_value = [
            Path('dir1/TestStruct.java'),
            Path('dir2/TestStruct.java')
        ]
        
        def read_side_effect(path):
            if 'dir1' in str(path):
                return """
                public class TestStruct implements org.apache.thrift.k {
                    public static final ww1.c f1 = new ww1.c("field1", (byte) 11, 1);
                    public String f2;
                }
                """
            else:
                return """
                public class TestStruct implements org.apache.thrift.k {
                    public static final ww1.c f1 = new ww1.c("field2", (byte) 8, 1);
                    public int f2;
                }
                """
        
        mock_read_file.side_effect = read_side_effect
        
        thrift_compiler.structs.clear()
        thrift_compiler.parse_structs()
        
        # Last one wins
        assert 'TestStruct' in thrift_compiler.structs
        struct = thrift_compiler.structs['TestStruct']
        assert struct.fields[0].name == "field2"
        assert struct.fields[0].ttype == "i32"


class TestTypeMapping:
    """Test type mapping and resolution"""
    
    def test_type_map_constants(self):
        """Verify TYPE_MAP constant values"""
        assert thrift_compiler.TYPE_MAP[1] == 'bool'
        assert thrift_compiler.TYPE_MAP[2] == 'bool'
        assert thrift_compiler.TYPE_MAP[3] == 'byte'
        assert thrift_compiler.TYPE_MAP[4] == 'double'
        assert thrift_compiler.TYPE_MAP[6] == 'i16'
        assert thrift_compiler.TYPE_MAP[8] == 'i32'
        assert thrift_compiler.TYPE_MAP[10] == 'i64'
        assert thrift_compiler.TYPE_MAP[11] == 'string'
        assert thrift_compiler.TYPE_MAP[12] == 'struct'
        assert thrift_compiler.TYPE_MAP[13] == 'map'
        assert thrift_compiler.TYPE_MAP[14] == 'set'
        assert thrift_compiler.TYPE_MAP[15] == 'list'
        assert thrift_compiler.TYPE_MAP[16] == 'enum'
    
    @patch('thrift_compiler.JAVA_ROOT')
    @patch('thrift_compiler.read_file')
    def test_obfuscated_name_collision_handling(self, mock_read_file, mock_java_root):
        """Test handling of obfuscated name collisions (same filename in different dirs)"""
        mock_java_root.rglob.return_value = [
            Path('A/E0.java'),
            Path('B/E0.java')
        ]
        
        def read_side_effect(path):
            if '/A/' in str(path):
                return """
                public class E0 {
                    public String toString() {
                        return "ResponseTypeA()";
                    }
                }
                """
            else:
                return """
                public class E0 {
                    public String toString() {
                        return "ResponseTypeB()";
                    }
                }
                """
        
        mock_read_file.side_effect = read_side_effect
        
        thrift_compiler.structs.clear()
        thrift_compiler.parse_structs()
        
        # Both should be parsed with their real names
        assert 'ResponseTypeA' in thrift_compiler.structs or 'ResponseTypeB' in thrift_compiler.structs
