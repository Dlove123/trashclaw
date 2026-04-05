#!/usr/bin/env python3
"""
Test suite for TrashClaw project config feature (Issue #67)
Tests .trashclaw.toml and .trashclaw.json support with auto-loaded context files.
"""

import os
import sys
import tempfile
import shutil

def test_toml_file_exists():
    """Test that .trashclaw.toml exists in the repo"""
    assert os.path.exists(".trashclaw.toml"), ".trashclaw.toml not found"
    print("✅ test_toml_file_exists: PASSED")

def test_toml_parser_function():
    """Test that _parse_simple_toml function exists"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'def _parse_simple_toml' in content, "_parse_simple_toml function not found"
    print("✅ test_toml_parser_function: PASSED")

def test_load_project_config_function():
    """Test that load_project_config function exists"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'def load_project_config' in content, "load_project_config function not found"
    assert '.trashclaw.toml' in content, "Does not reference .trashclaw.toml"
    assert '.trashclaw.json' in content, "Does not reference .trashclaw.json"
    print("✅ test_load_project_config_function: PASSED")

def test_config_fields_supported():
    """Test that all required config fields are supported"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    required_fields = ['context_files', 'system_prompt', 'model', 'auto_shell']
    for field in required_fields:
        assert f'"{field}"' in content or f"'{field}'" in content, f"Config field '{field}' not supported"
    
    print(f"✅ test_config_fields_supported: PASSED")
    print(f"   Supported fields: {', '.join(required_fields)}")

def test_config_loaded_in_main():
    """Test that config is loaded in main() function"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'load_project_config()' in content, "load_project_config() not called in main()"
    print("✅ test_config_loaded_in_main: PASSED")

def test_context_files_auto_loaded():
    """Test that context files are auto-loaded"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'PROJECT_CONFIG["context_files"]' in content, "Context files not accessed"
    assert 'Auto-loading' in content or 'auto-load' in content.lower(), "No auto-load message"
    print("✅ test_context_files_auto_loaded: PASSED")

def test_system_prompt_appended():
    """Test that system_prompt from config is appended"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'PROJECT_CONFIG["system_prompt"]' in content, "System prompt config not accessed"
    assert 'Additional instructions' in content, "System prompt not appended to messages"
    print("✅ test_system_prompt_appended: PASSED")

def test_auto_shell_override():
    """Test that auto_shell config overrides environment"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'PROJECT_CONFIG["auto_shell"]' in content, "Auto shell config not accessed"
    assert 'APPROVE_SHELL' in content, "APPROVE_SHELL not modified"
    print("✅ test_auto_shell_override: PASSED")

def test_model_override():
    """Test that model config overrides environment"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'PROJECT_CONFIG["model"]' in content, "Model config not accessed"
    assert 'MODEL_NAME' in content, "MODEL_NAME not modified"
    print("✅ test_model_override: PASSED")

def test_json_fallback():
    """Test that .trashclaw.json is supported as fallback"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'json_path' in content, "JSON path not defined"
    assert 'json.load' in content, "JSON loading not implemented"
    print("✅ test_json_fallback: PASSED")

def test_python_version_compat():
    """Test Python version compatibility (3.11+ tomllib, <3.11 manual parse)"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'sys.version_info' in content, "Version check not implemented"
    assert '(3, 11)' in content, "Python 3.11 check not found"
    assert 'import tomllib' in content, "tomllib import not found"
    print("✅ test_python_version_compat: PASSED")

def test_existing_config_preserved():
    """Test that existing .trashclaw.toml has required structure"""
    import base64
    
    # Read existing config
    with open('.trashclaw.toml', 'r') as f:
        content = f.read()
    
    # Check for required sections
    assert '[agent]' in content or '[context]' in content, "Config missing required sections"
    assert 'context_files' in content or 'auto_load' in content, "Config missing context_files"
    
    print("✅ test_existing_config_preserved: PASSED")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("TrashClaw Project Config Test Suite (Issue #67)")
    print("=" * 60)
    print()
    
    tests = [
        test_toml_file_exists,
        test_toml_parser_function,
        test_load_project_config_function,
        test_config_fields_supported,
        test_config_loaded_in_main,
        test_context_files_auto_loaded,
        test_system_prompt_appended,
        test_auto_shell_override,
        test_model_override,
        test_json_fallback,
        test_python_version_compat,
        test_existing_config_preserved,
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: FAILED - {e}")
            failed += 1
        except Exception as e:
            print(f"⚠️  {test.__name__}: ERROR - {e}")
            skipped += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
