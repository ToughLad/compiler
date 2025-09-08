#!/usr/bin/env python3
"""Additional tests for helpers, smali utilities, and reporting."""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
import thrift_compiler


def test_escape_reserved_and_identifiers():
    e = thrift_compiler.escape_reserved
    # Reserved words get suffixed
    assert e('map') == 'map_'
    assert e('throws') == 'throws_'
    assert e('i32') == 'i32_'
    assert e('async') == 'async_'
    # Starts with digit -> prefix
    assert e('123abc') == 'n_123abc'
    # Invalid chars replaced with underscore
    assert e('foo-bar') == 'foo_bar'
    assert e('foo bar') == 'foo_bar'


@pytest.mark.unit
def test_smali_descriptor_parser():
    s2j = thrift_compiler._smali_desc_to_java_simple
    assert s2j('Ljava/lang/String;') == 'String'
    assert s2j('Lcom/foo/Bar;') == 'Bar'
    assert s2j('Lcom/foo/Outer$Inner;') == 'Inner'
    assert s2j('I') == 'int'
    assert s2j('J') == 'long'
    assert s2j('S') == 'short'
    assert s2j('B') == 'byte'
    assert s2j('Z') == 'boolean'
    assert s2j('D') == 'double'
    assert s2j('F') == 'float'
    # Arrays fallback to binary
    assert s2j('[I') == 'binary'


def test_smali_roots_iterators_and_rel(monkeypatch, tmp_path):
    # Create fake smali root and file
    smali_root = tmp_path / 'smali_classesX'
    smali_root.mkdir()
    smali_file = smali_root / 'Lcom' / 'foo' / 'Bar.smali'
    smali_file.parent.mkdir(parents=True, exist_ok=True)
    smali_file.write_text('.class public Lcom/foo/Bar;\n.field public a:Ljava/lang/String;')

    # Point SMALI_ROOTS to our fake root
    monkeypatch.setattr(thrift_compiler, 'SMALI_ROOTS', [smali_root])
    # unrelated JAVA_ROOT to ensure _rel_to_any prefers smali root
    monkeypatch.setattr(thrift_compiler, 'JAVA_ROOT', tmp_path / 'java_root', raising=False)

    roots = list(thrift_compiler._iter_existing_smali_roots())
    assert smali_root in roots

    files = list(thrift_compiler._iter_smali_files())
    assert smali_file in files

    rel = thrift_compiler._rel_to_any(smali_file)
    assert rel == smali_file.relative_to(smali_root).as_posix()


def test_write_report_outputs(tmp_path, monkeypatch):
    # Prepare small state
    thrift_compiler.enums.clear()
    thrift_compiler.structs.clear()
    thrift_compiler.services.clear()
    thrift_compiler.alias_map.clear()
    thrift_compiler.exception_structs.clear()

    # Add one of each
    en = thrift_compiler.ThriftEnum('E')
    en.values.append(('A', 1))
    thrift_compiler.enums['E'] = en
    st = thrift_compiler.ThriftStruct('S')
    thrift_compiler.structs['S'] = st
    svc = thrift_compiler.ThriftService('Svc')
    svc.add_method('do', 'binary', 'void', [])
    thrift_compiler.services['Svc'] = svc
    thrift_compiler.alias_map['X1'] = 'X1'

    out = tmp_path / 'out.thrift'
    monkeypatch.setattr(thrift_compiler, 'OUTPUT_FILE', out, raising=False)

    thrift_compiler.write_report()

    j = out.with_suffix('.report.json')
    t = out.with_suffix('.report.txt')
    assert j.exists() and t.exists()
    data = json.loads(j.read_text())
    assert data['counts']['enums'] == 1
    assert data['counts']['structs'] == 1
    assert data['counts']['services'] == 1
    assert data['counts']['methods'] == 1
    assert data['counts']['aliases'] == 1
    # Incomplete because arg binary/ret void
    assert any(m['name'] == 'do' for m in data['incomplete_methods'])


def test_emit_thrift_reserved_and_throws(monkeypatch, tmp_path):
    # Reset state
    thrift_compiler.enums.clear()
    thrift_compiler.structs.clear()
    thrift_compiler.services.clear()
    thrift_compiler.alias_map.clear()
    thrift_compiler.exception_structs.clear()
    thrift_compiler.emitted_exception_names.clear()
    thrift_compiler.exception_name_alias.clear()

    # Known exception struct
    ex = thrift_compiler.ThriftStruct('KnownException')
    thrift_compiler.structs['KnownException'] = ex
    thrift_compiler.exception_structs.add('KnownException')
    thrift_compiler.emitted_exception_names.add('KnownException')

    # Service with reserved method name and mixed exceptions
    svc = thrift_compiler.ThriftService('S')
    svc.add_method('map', 'binary', 'void', exceptions=['UnknownEx', 'KnownException'])
    thrift_compiler.services['S'] = svc

    out = tmp_path / 'emit.thrift'
    monkeypatch.setattr(thrift_compiler, 'OUTPUT_FILE', out, raising=False)

    thrift_compiler.emit_thrift()
    c = out.read_text()
    assert 'service S {' in c
    # method name escaped
    assert 'void map_(1: binary request)' in c
    # only KnownException included in throws
    assert 'throws (1: KnownException ex)' in c


def test_parse_services_with_wrappers(monkeypatch, tmp_path):
    # Setup temporary JAVA_ROOT with minimal files
    root = tmp_path / 'sources'
    root.mkdir()
    (root / 'services').mkdir()
    # Client with b("doThing")
    (root / 'services' / 'FooService$Client.java').write_text(
        'public class FooService$Client { public final void doThing(){ b("doThing"); } }'
    )
    # args wrapper with public field type and toString pattern
    (root / 'services' / 'U8.java').write_text(
        'public class U8 { public java.lang.String f1; public String toString(){ return new StringBuilder("doThing_args(").toString(); } }'
    )
    # result wrapper with success/exception and toString pattern
    (root / 'services' / 'V8.java').write_text(
        'public class V8 { public FooResponse success; public FooException ex; public String toString(){ return new StringBuilder("doThing_result(").toString(); } }'
    )

    # Prepare structs (response known, exception recognized)
    thrift_compiler.structs.clear()
    thrift_compiler.services.clear()
    thrift_compiler.exception_structs.clear()
    thrift_compiler.structs['FooResponse'] = thrift_compiler.ThriftStruct('FooResponse')
    thrift_compiler.exception_structs.add('FooException')

    # Point compiler to our temp JAVA_ROOT
    monkeypatch.setattr(thrift_compiler, 'JAVA_ROOT', root, raising=False)

    thrift_compiler.parse_services()

    assert 'FooService' in thrift_compiler.services
    svc = thrift_compiler.services['FooService']
    assert any(m['name'] == 'doThing' for m in svc.methods)
    m = [m for m in svc.methods if m['name'] == 'doThing'][0]
    # arg type normalized name
    assert m['arg_type'] in ('String', 'string')
    # Ret type remains 'void' from signature; wrappers are used primarily for inferring when missing
    assert m['ret_type'] == 'void'
    # Exceptions are attached when derivable from result wrappers in absence of better info.
    # Here, signature parsing dominates and exceptions remain empty.
    assert m['exceptions'] == []
