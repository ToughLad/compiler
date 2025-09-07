"""Pytest configuration and fixtures for thrift_compiler tests"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path for all tests
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def mock_java_root(temp_dir):
    """Create a mock Java source root directory"""
    java_root = temp_dir / 'sources'
    java_root.mkdir()
    return java_root


@pytest.fixture
def sample_enum_java():
    """Sample enum Java code"""
    return """
public enum TestEnum {
    VALUE1(1),
    VALUE2(2),
    VALUE3(3);
}
"""


@pytest.fixture
def sample_struct_java():
    """Sample struct Java code"""
    return """
public class TestStruct implements org.apache.thrift.k {
    public static final ww1.c f1 = new ww1.c("field1", (byte) 11, 1);
    public static final ww1.c f2 = new ww1.c("field2", (byte) 8, 2);
    public String f3;
    public int f4;
}
"""


@pytest.fixture
def sample_exception_java():
    """Sample exception Java code"""
    return """
public class TestException extends org.apache.thrift.i implements org.apache.thrift.k {
    public static final ww1.c f1 = new ww1.c("message", (byte) 11, 1);
    public String f2;
}
"""


@pytest.fixture
def sample_service_java():
    """Sample service Java code"""
    return """
public static class Client {
    public final TestResponse testMethod(TestRequest request) throws TestException {
        b("testMethod");
    }
}
"""


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset global state before each test"""
    import thrift_compiler
    thrift_compiler.enums.clear()
    thrift_compiler.structs.clear()
    thrift_compiler.services.clear()
    thrift_compiler.exception_structs.clear()
    thrift_compiler.alias_map.clear()
    thrift_compiler.class_index = {}
    if hasattr(thrift_compiler, 'response_map'):
        thrift_compiler.response_map = {}
    yield
    # Cleanup after test
    thrift_compiler.enums.clear()
    thrift_compiler.structs.clear()
    thrift_compiler.services.clear()
    thrift_compiler.exception_structs.clear()
    thrift_compiler.alias_map.clear()
    thrift_compiler.class_index = {}
