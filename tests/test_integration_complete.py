#!/usr/bin/env python3
"""Complete integration tests for thrift_compiler.py"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import thrift_compiler


class TestE2EEIntegration:
    """Integration tests for E2EE components extraction"""
    
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
    def test_e2ee_components_extraction(self, mock_output, mock_root):
        """Test extraction of E2EE components"""
        mock_root.return_value = self.java_root
        mock_root.exists.return_value = True
        mock_root.rglob = self.java_root.rglob
        mock_output.return_value = self.output_file
        
        # Create E2EE enum
        self.create_java_file('enums/TalkErrorCode.java', '''
public enum TalkErrorCode {
    E2EE_INVALID_PROTOCOL(81),
    E2EE_RETRY_ENCRYPT(82),
    E2EE_UPDATE_SENDER_KEY(83),
    E2EE_UPDATE_RECEIVER_KEY(84);
}
''')
        
        # Create E2EE structs
        self.create_java_file('structs/EstablishE2EESessionRequest.java', '''
public class EstablishE2EESessionRequest implements org.apache.thrift.k {
    public static final ww1.c f1 = new ww1.c("clientPublicKey", (byte) 11, 1);
    public String f2;
}
''')
        
        self.create_java_file('structs/EstablishE2EESessionResponse.java', '''
public class EstablishE2EESessionResponse implements org.apache.thrift.k {
    public static final ww1.c f1 = new ww1.c("sessionId", (byte) 11, 1);
    public static final ww1.c f2 = new ww1.c("serverPublicKey", (byte) 11, 2);
    public static final ww1.c f3 = new ww1.c("expireAt", (byte) 10, 3);
    public String f4;
    public String f5;
    public long f6;
}
''')
        
        # Create E2EE service
        self.create_java_file('services/E2eeKeyBackupService.java', '''public class E2eeKeyBackupService {}''')
        self.create_java_file('services/E2eeKeyBackupService$Client.java', '''
public static class Client {
    public final void callWithResult(binary request) {
        b("callWithResult");
    }
}
''')
        
        # Run compiler
        thrift_compiler.main()
        
        # Verify E2EE content
        content = self.output_file.read_text()
        
        # Check E2EE error codes
        assert 'E2EE_INVALID_PROTOCOL = 81' in content
        assert 'E2EE_RETRY_ENCRYPT = 82' in content
        assert 'E2EE_UPDATE_SENDER_KEY = 83' in content
        
        # Check E2EE structs
        assert 'struct EstablishE2EESessionRequest {' in content
        assert '1: string clientPublicKey' in content
        
        assert 'struct EstablishE2EESessionResponse {' in content
        assert '1: string sessionId' in content
        assert '2: string serverPublicKey' in content
        assert '3: i64 expireAt' in content
        
        # Check E2EE service
        assert 'service E2eeKeyBackupService {' in content
        assert 'void callWithResult(1: binary request)' in content
    
    @patch('thrift_compiler.JAVA_ROOT')
    @patch('thrift_compiler.OUTPUT_FILE')
    def test_complex_type_resolution(self, mock_output, mock_root):
        """Test resolution of complex nested types"""
        mock_root.return_value = self.java_root
        mock_root.exists.return_value = True
        mock_root.rglob = self.java_root.rglob
        mock_output.return_value = self.output_file
        
        # Create struct with complex types
        self.create_java_file('structs/ComplexData.java', '''
public class ComplexData implements org.apache.thrift.k {
    public static final ww1.c f1 = new ww1.c("mapData", (byte) 13, 1);
    public static final ww1.c f2 = new ww1.c("listData", (byte) 15, 2);
    public static final ww1.c f3 = new ww1.c("setData", (byte) 14, 3);
    public static final ww1.c f4 = new ww1.c("nestedMap", (byte) 13, 4);
    public HashMap<String, Integer> f5;
    public ArrayList<User> f6;
    public HashSet<String> f7;
    public HashMap<String, ArrayList<User>> f8;
}
''')
        
        # Run compiler
        thrift_compiler.main()
        
        # Verify complex types
        content = self.output_file.read_text()
        
        assert 'struct ComplexData {' in content
        # Unknown custom types are normalized to primitives in output
        assert '1: map<string,i32> mapData' in content
        # User is not defined in this test, falls back to i32
        assert '2: list<i32> listData' in content
        assert '3: set<string> setData' in content
        assert '4: map<string,i32> nestedMap' in content
    
    @patch('thrift_compiler.JAVA_ROOT')
    def test_empty_project(self, mock_root):
        """Test compilation with no Java files"""
        mock_root.return_value = self.java_root
        mock_root.exists.return_value = True
        mock_root.rglob = self.java_root.rglob
        
        # Run compiler with no files
        with patch('thrift_compiler.OUTPUT_FILE', self.output_file):
            thrift_compiler.main()
        
        # Should create empty thrift file
        assert self.output_file.exists()
        content = self.output_file.read_text()
        
        # Should have headers but no definitions
        assert '# Enums' in content
        assert '# Structs' in content
        assert '# Services' in content
        
        # Should not have any actual definitions
        assert 'enum ' not in content
        assert 'struct ' not in content
        assert 'service ' not in content
    
    @patch('thrift_compiler.JAVA_ROOT')
    @patch('thrift_compiler.OUTPUT_FILE')
    def test_large_scale_extraction(self, mock_output, mock_root):
        """Test extraction with many files to verify performance"""
        mock_root.return_value = self.java_root
        mock_root.exists.return_value = True
        mock_root.rglob = self.java_root.rglob
        mock_output.return_value = self.output_file
        
        # Create 100 structs
        for i in range(100):
            self.create_java_file(f'structs/Struct{i}.java', f'''
public class Struct{i} implements org.apache.thrift.k {{
    public static final ww1.c f1 = new ww1.c("field{i}", (byte) 11, 1);
    public String f2;
}}
''')
        
        # Create 50 enums
        for i in range(50):
            self.create_java_file(f'enums/Enum{i}.java', f'''
public enum Enum{i} {{
    VALUE1({i}0),
    VALUE2({i}1),
    VALUE3({i}2);
}}
''')
        
        # Create 20 services
        for i in range(20):
            self.create_java_file(f'services/Service{i}.java', f'public class Service{i} {{}}')
            self.create_java_file(f'services/Service{i}$Client.java', f'''
public static class Client {{
    public final void method{i}(Struct{i} request) {{
        b("method{i}");
    }}
}}
''')
        
        # Run compiler
        thrift_compiler.main()
        
        # Verify all components were extracted
        content = self.output_file.read_text()
        
        # Check structs
        for i in range(100):
            assert f'struct Struct{i} {{' in content
            assert f'1: string field{i}' in content
        
        # Check enums
        for i in range(50):
            assert f'enum Enum{i} {{' in content
            assert f'VALUE1 = {i}0' in content
        
        # Check services
        for i in range(20):
            assert f'service Service{i} {{' in content
            assert f'void method{i}(1: Struct{i} request)' in content
