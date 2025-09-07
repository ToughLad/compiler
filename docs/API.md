# Thrift Compiler API Documentation

## Core Classes

### `ThriftEnum`
Represents a Thrift enumeration type.

**Attributes:**
- `name` (str): Enum name
- `values` (list): List of (name, value) tuples

### `ThriftStruct`
Represents a Thrift struct or exception.

**Attributes:**
- `name` (str): Struct name
- `fields` (list): List of Field objects

### `ThriftService`
Represents a Thrift service definition.

**Attributes:**
- `name` (str): Service name
- `methods` (list): List of method dictionaries

**Methods:**
- `add_method(name, arg_type, ret_type, exceptions)`: Add a method to the service

### `Field`
Represents a struct field.

**Attributes:**
- `id` (int): Field ID
- `name` (str): Field name
- `ttype` (str): Thrift type
- `type_name` (str): Resolved type name
- `key_type` (str): Map key type (if applicable)
- `val_type` (str): Map value type (if applicable)
- `required` (bool): Whether field is required

## Core Functions

### `parse_enums()`
Parses all enum definitions from Java sources.

**Returns:** None (populates global `enums` dict)

### `parse_structs()`
Parses all struct definitions from Java sources.

**Process:**
1. Builds obfuscated name mappings using toString() patterns
2. Parses field constants and member variables
3. Resolves complex types (lists, maps, sets)
4. Creates ThriftStruct instances

**Returns:** None (populates global `structs` dict)

### `parse_services()`
Parses all service definitions from Java sources.

**Process:**
1. Builds class index for all Java files
2. Creates response/request mappings
3. Scans for wrapper patterns
4. Extracts service methods with proper typing

**Returns:** None (populates global `services` dict)

### `write_thrift()`
Writes the complete Thrift IDL to output file.

**Sections:**
1. Type aliases for obfuscated names
2. Enum definitions
3. Struct and exception definitions
4. Service definitions

### `normalize_type_name(type_str)`
Normalizes Java type names to clean identifiers.

**Parameters:**
- `type_str` (str): Java type string

**Returns:** 
- str: Normalized type name or None

### `thrift_type_str(field)`
Converts a Field object to Thrift type string.

**Parameters:**
- `field` (Field): Field object

**Returns:**
- str: Thrift type representation

## Global Registries

### `enums`
Dictionary mapping enum names to ThriftEnum objects.

### `structs`
Dictionary mapping struct names to ThriftStruct objects.

### `services`
Dictionary mapping service names to ThriftService objects.

### `exception_structs`
Set of struct names that are exceptions.

### `alias_map`
Dictionary mapping obfuscated names to clean aliases.

### `response_map`
Dictionary mapping file paths to Response/Request type names.

## Configuration

### Constants
- `JAVA_ROOT`: Path to decompiled Java sources
- `OUTPUT_FILE`: Path to output Thrift file

### Type Mapping
```python
TYPE_MAP = {
    1: 'bool', 2: 'bool', 3: 'byte', 4: 'double',
    6: 'i16', 8: 'i32', 10: 'i64', 11: 'string',
    12: 'struct', 13: 'map', 14: 'set', 15: 'list', 16: 'enum'
}
```

## Usage Examples

### Basic Usage
```python
from thrift_compiler import main

# Run the compiler
main()
```

### Programmatic Usage
```python
from thrift_compiler import parse_enums, parse_structs, parse_services, write_thrift

# Parse components
parse_enums()
parse_structs()
parse_services()

# Write output
write_thrift()
```

### Custom Output Path
```python
from thrift_compiler import OUTPUT_FILE
from pathlib import Path

# Change output path
OUTPUT_FILE = Path('/custom/path/output.thrift')
```
