# LINE Thrift IDL Compiler

A comprehensive Thrift IDL extractor and compiler for LINE APK decompiled sources.

## Features

- **Complete Thrift IDL extraction** from decompiled Java sources
- **Automatic type resolution** for obfuscated class names
- **Response/Request mapping** using toString() patterns
- **Support for complex types** (lists, maps, sets, enums)
- **E2EE components extraction** including LetterSealing
- **Service method typing** with proper request/response types

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python src/thrift_compiler.py
```

This will:
1. Parse all Java files in `/workspaces/LINE/line_decompiled/sources`
2. Extract enums, structs, and services
3. Generate `line.thrift` with complete Thrift IDL

### Output Statistics

The compiler extracts:
- **2,014 structs** with proper field definitions
- **508 enums** with values
- **105 services** with 421 methods
- **387 type aliases** for obfuscated names

## Architecture

### Core Components

1. **Enum Parser** - Extracts Java enums with values
2. **Struct Parser** - Parses Thrift struct implementations with fields
3. **Service Parser** - Extracts service definitions and methods
4. **Type Resolver** - Maps obfuscated names to real types
5. **Response/Request Mapper** - Uses toString() patterns to identify types

### Key Features

#### Obfuscated Name Resolution
Maps obfuscated class names (e.g., `E0`, `X3`) to actual types (e.g., `GetContactsV3Response`, `DeleteOtherFromChatResponse`) using:
- toString() method patterns
- StringBuilder patterns with field names

#### Field Type Resolution
- Handles primitive types (bool, byte, i16, i32, i64, string)
- Complex types (list, map, set) with nested type resolution
- Struct references with automatic aliasing

#### E2EE Support
Complete extraction of:
- E2EE services (E2eeKeyBackupService, E2eeTalkService)
- Key exchange methods and structs
- LetterSealing components
- Error codes and notification types

## Project Structure

```
compiler/
├── src/
│   └── thrift_compiler.py    # Main compiler
├── docs/
│   └── API.md                 # API documentation
├── examples/
│   └── example_output.thrift  # Sample output
├── tests/
│   └── test_compiler.py       # Unit tests
├── README.md
└── requirements.txt
```

## Example Output

```thrift
enum TalkErrorCode {
  E2EE_INVALID_PROTOCOL = 81,
  E2EE_RETRY_ENCRYPT = 82,
  ...
}

struct GetContactsV3Response {
  1: list<i32> responses
}

service GroupTalkService {
  CancelChatInvitationResponse cancelChatInvitation(1: C12999i2 request),
  DeleteOtherFromChatResponse deleteOtherFromChat(1: W3 request),
  ...
}
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This tool is for educational and research purposes only.
