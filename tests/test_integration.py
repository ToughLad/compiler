#!/usr/bin/env python3
"""Integration tests for thrift_compiler.py"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import thrift_compiler


class TestIntegration:
    """Integration tests for end-to-end scenarios"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.java_root = Path(self.temp_dir) / 'sources'
        self.java_root.mkdir()
        self.output_file = Path(self.temp_dir) / 'output.thrift'
        
        # Clear global state
        thrift_compiler.enums.clear()
        thrift_compiler.structs.clear()
        thrift_compiler.services.clear()
        thrift_compiler.exception_structs.clear()
        thrift_compiler.alias_map.clear()
        thrift_compiler.class_index = {}
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_java_file(self, rel_path, content):
        """Helper to create Java file in test directory"""
        file_path = self.java_root / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path
    
    @patch('thrift_compiler.JAVA_ROOT')
    @patch('thrift_compiler.OUTPUT_FILE')
    def test_complete_compilation(self, mock_output, mock_root):
        """Test complete compilation from Java sources to Thrift IDL"""
        mock_root.return_value = self.java_root
        mock_root.exists.return_value = True
        mock_root.rglob = self.java_root.rglob
        mock_output.return_value = self.output_file
        
        # Create test enum
        self.create_java_file('enums/Status.java', '''
public enum Status {
    ACTIVE(1),
    INACTIVE(2),
    PENDING(3);
}
''')
        
        # Create test struct
        self.create_java_file('structs/User.java', '''
public class User implements org.apache.thrift.k {
    public static final ww1.c f1 = new ww1.c("id", (byte) 10, 1);
    public static final ww1.c f2 = new ww1.c("name", (byte) 11, 2);
    public static final ww1.c f3 = new ww1.c("status", (byte) 16, 3);
    public long f4;
    public String f5;
    public Status f6;
}
''')
        
        # Create test exception
        self.create_java_file('exceptions/UserException.java', '''
public class UserException extends org.apache.thrift.i implements org.apache.thrift.k {
    public static final ww1.c f1 = new ww1.c("message", (byte) 11, 1);
    public static final ww1.c f2 = new ww1.c("code", (byte) 8, 2);
    public String f3;
    public int f4;
}
''')
        
        # Create test service
        self.create_java_file('services/UserService.java', '''public class UserService {}''')
        self.create_java_file('services/UserService$Client.java', '''
public static class Client {
    public final User getUser(long userId) throws UserException {
        b("getUser");
    }
    public final void updateUser(User user) throws UserException {
        b("updateUser");
    }
}
''')
        
        # Create obfuscated Response class
        self.create_java_file('B41/E0.java', '''
public class E0 implements org.apache.thrift.d {
    public static final ww1.c f1 = new ww1.c("users", (byte) 15, 1);
    public ArrayList<User> f2;
    public String toString() {
        return new StringBuilder("GetUsersResponse(").toString();
    }
}
''')
        
        # Run compiler
        thrift_compiler.main()
        
        # Verify output file was created
        assert self.output_file.exists()
        
        # Read and verify content
        content = self.output_file.read_text()
        
        # Check enum
        assert 'enum Status {' in content
        assert 'ACTIVE = 1' in content
        assert 'INACTIVE = 2' in content
        assert 'PENDING = 3' in content
        
        # Check struct
        assert 'struct User {' in content
        assert '1: i64 id' in content
        assert '2: string name' in content
        assert '3: enum status' in content
        
        # Check exception
        assert 'exception UserException {' in content
        assert '1: string message' in content
        assert '2: i32 code' in content
        
        # Check service
        assert 'service UserService {' in content
        assert 'User getUser(1: i64 request)' in content
        assert 'void updateUser(1: User request)' in content
        
        # Check obfuscated response
        assert 'struct GetUsersResponse {' in content
        assert '1: list<User> users' in content