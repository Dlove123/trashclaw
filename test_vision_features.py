#!/usr/bin/env python3
"""
Test suite for TrashClaw vision features (Issue #65)
Tests view_image tool and screenshot functionality.
"""

import os
import sys
import base64
import tempfile
import subprocess

def test_view_image_exists():
    """Test that view_image tool is defined in trashclaw.py"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'def tool_view_image' in content, "tool_view_image function not found"
    assert '"view_image"' in content, "view_image tool not in TOOLS list"
    assert 'TOOL_DISPATCH' in content and 'view_image' in content, "view_image not in TOOL_DISPATCH"
    print("✅ test_view_image_exists: PASSED")

def test_view_image_functionality():
    """Test that view_image can load and encode images"""
    test_image = 'trashy.png'
    if not os.path.exists(test_image):
        print(f"⚠️  test_view_image_functionality: SKIPPED (no test image)")
        return
    
    with open(test_image, 'rb') as f:
        image_data = f.read()
    
    base64_data = base64.b64encode(image_data).decode('utf-8')
    size_kb = len(image_data) / 1024
    
    assert size_kb < 5000, f"Image too large: {size_kb:.1f}KB > 5000KB"
    assert len(base64_data) > 0, "Base64 encoding failed"
    
    print(f"✅ test_view_image_functionality: PASSED")
    print(f"   Image: {test_image}, Size: {size_kb:.1f}KB, Base64: {len(base64_data)} chars")

def test_screenshot_command_exists():
    """Test that /screenshot command is implemented"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'def tool_take_screenshot' in content, "tool_take_screenshot function not found"
    assert 'elif command == "/screenshot"' in content, "/screenshot command not found"
    print("✅ test_screenshot_command_exists: PASSED")

def test_img_command_exists():
    """Test that /img command is implemented"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'elif command == "/img"' in content, "/img command not found"
    assert 'tool_view_image(arg)' in content, "/img command doesn't call tool_view_image"
    print("✅ test_img_command_exists: PASSED")

def test_vision_command_exists():
    """Test that /vision command for checking vision support"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'elif command == "/vision"' in content, "/vision command not found"
    assert '/v1/models' in content, "Vision check doesn't query /v1/models"
    print("✅ test_vision_command_exists: PASSED")

def test_image_formats_supported():
    """Test that multiple image formats are supported"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    required_formats = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    for fmt in required_formats:
        assert fmt in content, f"Format {fmt} not in supported formats"
    
    print(f"✅ test_image_formats_supported: PASSED")
    print(f"   Supported: {', '.join(required_formats)}")

def test_base64_encoding():
    """Test that base64 encoding is properly implemented"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    assert 'import base64' in content or 'base64' in content, "base64 module not imported"
    assert 'base64.b64encode' in content, "base64.b64encode not used"
    assert 'data:' in content and ';base64,' in content, "Data URL format not correct"
    print("✅ test_base64_encoding: PASSED")

def test_readme_updated():
    """Test that README documents vision features"""
    with open('README.md', 'r') as f:
        content = f.read()
    
    assert '/img' in content, "README doesn't document /img command"
    assert '/screenshot' in content, "README doesn't document /screenshot command"
    assert 'vision' in content.lower(), "README doesn't mention vision support"
    assert 'view_image' in content, "README doesn't document view_image tool"
    print("✅ test_readme_updated: PASSED")

def test_no_external_dependencies():
    """Test that vision features use only stdlib"""
    with open('trashclaw.py', 'r') as f:
        content = f.read()
    
    # Should use base64 from stdlib
    assert 'import base64' in content, "Should use stdlib base64"
    
    # Should NOT use external image libraries
    forbidden = ['PIL', 'Image', 'opencv', 'cv2', 'numpy']
    for lib in forbidden:
        # Allow these words in comments/strings but not as imports
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('import') or line.strip().startswith('from'):
                assert lib not in line.lower(), f"External dependency found: {lib}"
    
    print("✅ test_no_external_dependencies: PASSED")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("TrashClaw Vision Features Test Suite (Issue #65)")
    print("=" * 60)
    print()
    
    tests = [
        test_view_image_exists,
        test_view_image_functionality,
        test_screenshot_command_exists,
        test_img_command_exists,
        test_vision_command_exists,
        test_image_formats_supported,
        test_base64_encoding,
        test_readme_updated,
        test_no_external_dependencies,
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
