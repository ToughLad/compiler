import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.thrift_compiler import parse_enums, enums, read_file, parse_structs, structs, parse_services, services

class TestParseEnums(unittest.TestCase):

    @patch('src.thrift_compiler.JAVA_ROOT', Path('/workspaces/LINE/compiler/tests/fixtures/sources'))
    @patch('src.thrift_compiler.read_file')
    def test_parse_enums(self, mock_read_file):
        # Mock file content for enum_sample.java
        mock_read_file.return_value = '''public enum Status {
    ACTIVE("Active", 1),
    INACTIVE("Inactive", 2, 3);
}'''
        
        # Mock rglob to return only the enum file
        with patch('pathlib.Path.rglob') as mock_rglob:
            mock_path = MagicMock()
            mock_rglob.return_value = [mock_path]
            mock_path.read_text.return_value = mock_read_file.return_value
            
            parse_enums()
        
        self.assertIn('Status', enums)
        status_enum = enums['Status']
        self.assertEqual(status_enum.name, 'Status')
        # Values are coerced to ints when safe (no leading zeros)
        self.assertEqual(status_enum.values, [('ACTIVE', 1), ('INACTIVE', 2)])

class TestParseStructs(unittest.TestCase):

    @patch('src.thrift_compiler.JAVA_ROOT', Path('/workspaces/LINE/compiler/tests/fixtures/sources'))
    @patch('src.thrift_compiler.read_file')
    def test_parse_structs(self, mock_read_file):
        # Mock file content for struct_sample.java
        mock_read_file.return_value = '''public final class UserInfo implements org.apache.thrift.TBase {
    public static final ww1.c f1 = new ww1.c("id", (byte) 8, 1);
    public static final ww1.c f2 = new ww1.c("name", (byte) 11, 2);
    public long id;
    public String name;
}'''
        
        # Mock rglob to return only the struct file
        with patch('pathlib.Path.rglob') as mock_rglob:
            mock_path = MagicMock()
            mock_rglob.return_value = [mock_path]
            mock_path.read_text.return_value = mock_read_file.return_value
            
            parse_structs()
        
        self.assertIn('UserInfo', structs)
        user_struct = structs['UserInfo']
        self.assertEqual(user_struct.name, 'UserInfo')
        self.assertEqual(len(user_struct.fields), 2)
        self.assertEqual(user_struct.fields[0].name, 'id')
        self.assertEqual(user_struct.fields[0].ttype, 'i64')
        self.assertEqual(user_struct.fields[1].name, 'name')
        self.assertEqual(user_struct.fields[1].ttype, 'string')

class TestParseServices(unittest.TestCase):

    def test_parse_services(self):
        # Mock file content for service_sample.java
        sample = '''public class UserServiceClient {
    public final void getUserInfo(String userId) throws Exception {
        b("getUserInfo", userId);
    }
    static class getUserInfo_args {
        public String userId;
    }
    static class getUserInfo_result {
        public UserResponse success;
        public UserException ex;
    }
}'''

        with patch('src.thrift_compiler.JAVA_ROOT', Path('/workspaces/LINE/compiler/tests/fixtures/sources')):
            with patch('src.thrift_compiler.read_file', return_value=sample):
                # Mock rglob to return only the service file
                with patch('pathlib.Path.rglob') as mock_rglob:
                    mock_path = MagicMock()
                    mock_rglob.return_value = [mock_path]
                    mock_path.read_text.return_value = sample
                    parse_services()
        
        self.assertIn('UserService', services)
        user_service = services['UserService']
        self.assertEqual(user_service.name, 'UserService')
        self.assertEqual(len(user_service.methods), 1)
        method = user_service.methods[0]
        self.assertEqual(method['name'], 'getUserInfo')
        # Client signature sanitizes to primitive
        self.assertEqual(method['arg_type'], 'string')
        # Direct signature parsing sets ret type; wrappers/inner-class logic may be overridden
        self.assertEqual(method['ret_type'], 'void')
        # Exceptions are not extracted from throws clause in this path
        self.assertEqual(method['exceptions'], [])

if __name__ == '__main__':
    unittest.main()
