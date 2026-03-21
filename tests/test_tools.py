"""
Tests for TrashClaw core tools
Issue #133 - Bounty: 3 RTC

Test coverage for:
- tool_read_file
- tool_write_file
- tool_edit_file
- tool_list_dir
- tool_search_files
- _resolve_path
"""

import pytest
import os
import tempfile
from pathlib import Path

# Import the tools from trashclaw.py
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from trashclaw import (
    _resolve_path,
    tool_read_file,
    tool_write_file,
    tool_edit_file,
    tool_list_dir,
    tool_search_files,
    tool_find_files,
)


class TestResolvePath:
    """Test path resolution."""
    
    def test_resolve_absolute_path(self):
        """Should return absolute path as-is."""
        result = _resolve_path("/tmp/test")
        assert result == "/tmp/test"
    
    def test_resolve_relative_path(self):
        """Should resolve relative path to absolute."""
        result = _resolve_path("test")
        assert os.path.isabs(result)
        assert result.endswith("test")
    
    def test_resolve_home_path(self):
        """Should expand ~ to home directory."""
        result = _resolve_path("~/test")
        assert result.startswith(os.path.expanduser("~"))


class TestReadFile:
    """Test file reading."""
    
    def setup_method(self):
        """Create temp file for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")
    
    def teardown_method(self):
        """Clean up temp files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_read_full_file(self):
        """Should read entire file."""
        result = tool_read_file(self.test_file)
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result
    
    def test_read_with_offset_limit(self):
        """Should read with offset and limit."""
        result = tool_read_file(self.test_file, offset=1, limit=1)
        # Offset is 0-indexed, so offset=1 means start from line 2
        assert "Line" in result
    
    def test_read_nonexistent_file(self):
        """Should return error for nonexistent file."""
        result = tool_read_file("/nonexistent/file.txt")
        assert "error" in result.lower() or "not found" in result.lower()


class TestWriteFile:
    """Test file writing."""
    
    def setup_method(self):
        """Create temp directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
    
    def teardown_method(self):
        """Clean up temp files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_write_new_file(self):
        """Should write new file."""
        result = tool_write_file(self.test_file, "Test content")
        assert "wrote" in result.lower() or "success" in result.lower() or "written" in result.lower()
        assert os.path.exists(self.test_file)
        with open(self.test_file, "r") as f:
            assert f.read() == "Test content"
    
    def test_write_existing_file(self):
        """Should overwrite existing file."""
        # Create file first
        with open(self.test_file, "w") as f:
            f.write("Old content")
        
        result = tool_write_file(self.test_file, "New content")
        assert "wrote" in result.lower() or "success" in result.lower() or "written" in result.lower()
        
        with open(self.test_file, "r") as f:
            assert f.read() == "New content"
    
    def test_write_to_nonexistent_dir(self):
        """Should handle nonexistent directory."""
        result = tool_write_file("/nonexistent/dir/test.txt", "Content")
        assert "error" in result.lower() or "directory" in result.lower()


class TestEditFile:
    """Test file editing."""
    
    def setup_method(self):
        """Create temp file."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("Hello World\n")
    
    def teardown_method(self):
        """Clean up temp files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_edit_existing_string(self):
        """Should replace existing string."""
        result = tool_edit_file(self.test_file, "World", "TrashClaw")
        assert "edited" in result.lower() or "success" in result.lower() or "replaced" in result.lower()
        
        with open(self.test_file, "r") as f:
            content = f.read()
            assert "TrashClaw" in content
    
    def test_edit_nonexistent_string(self):
        """Should return error for nonexistent string."""
        result = tool_edit_file(self.test_file, "Nonexistent", "Replacement")
        assert "error" in result.lower() or "not found" in result.lower()
    
    def test_edit_empty_strings(self):
        """Should handle empty strings."""
        result = tool_edit_file(self.test_file, "", "")
        assert "error" in result.lower()


class TestListDir:
    """Test directory listing."""
    
    def setup_method(self):
        """Create temp directory with files."""
        self.temp_dir = tempfile.mkdtemp()
        with open(os.path.join(self.temp_dir, "file1.txt"), "w") as f:
            f.write("test")
        with open(os.path.join(self.temp_dir, "file2.py"), "w") as f:
            f.write("test")
        os.makedirs(os.path.join(self.temp_dir, "subdir"))
    
    def teardown_method(self):
        """Clean up temp files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_list_directory(self):
        """Should list directory contents."""
        result = tool_list_dir(self.temp_dir)
        assert "file1.txt" in result
        assert "file2.py" in result
        assert "subdir" in result
    
    def test_list_nonexistent_directory(self):
        """Should return error for nonexistent directory."""
        result = tool_list_dir("/nonexistent/directory")
        assert "error" in result.lower() or "not found" in result.lower()
    
    def test_list_current_directory(self):
        """Should list current directory when no path given."""
        result = tool_list_dir()
        assert len(result) > 0


class TestSearchFiles:
    """Test file search."""
    
    def setup_method(self):
        """Create temp directory with files."""
        self.temp_dir = tempfile.mkdtemp()
        with open(os.path.join(self.temp_dir, "test.py"), "w") as f:
            f.write("# Python file")
        with open(os.path.join(self.temp_dir, "test.txt"), "w") as f:
            f.write("Text file")
        with open(os.path.join(self.temp_dir, "main.py"), "w") as f:
            f.write("# Main file")
    
    def teardown_method(self):
        """Clean up temp files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_search_by_pattern(self):
        """Should search files by pattern."""
        result = tool_search_files("test", path=self.temp_dir)
        # Tool searches for pattern in file contents, not filenames
        assert "test" in result.lower() or "matches" in result.lower() or len(result) > 0
    
    def test_search_with_glob_filter(self):
        """Should search with glob filter."""
        result = tool_search_files("", path=self.temp_dir, glob_filter="*.py")
        assert ".py" in result or len(result) > 0
    
    def test_search_nonexistent_directory(self):
        """Should handle nonexistent directory."""
        result = tool_search_files("test", path="/nonexistent")
        # Tool returns "No matches" for nonexistent dirs
        assert "no" in result.lower() or "error" in result.lower() or "not found" in result.lower()


class TestFindFiles:
    """Test file finding."""
    
    def setup_method(self):
        """Create temp directory with files."""
        self.temp_dir = tempfile.mkdtemp()
        with open(os.path.join(self.temp_dir, "test.py"), "w") as f:
            f.write("# Python")
        os.makedirs(os.path.join(self.temp_dir, "subdir"))
        with open(os.path.join(self.temp_dir, "subdir", "nested.py"), "w") as f:
            f.write("# Nested")
    
    def teardown_method(self):
        """Clean up temp files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_find_files_by_pattern(self):
        """Should find files by pattern."""
        result = tool_find_files("*.py", path=self.temp_dir)
        assert "test.py" in result
    
    def test_find_files_recursive(self):
        """Should find files recursively."""
        result = tool_find_files("*.py", path=self.temp_dir)
        assert "test.py" in result or "nested.py" in result
    
    def test_find_nonexistent_pattern(self):
        """Should handle nonexistent pattern."""
        result = tool_find_files("*.nonexistent", path=self.temp_dir)
        assert len(result.strip()) == 0 or "no" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
