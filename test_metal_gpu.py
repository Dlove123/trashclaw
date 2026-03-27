#!/usr/bin/env python3
"""
Test suite for Metal GPU acceleration
Bounty #38 - 15 RTC
"""

import pytest
import sys
import platform
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the module under test
from metal_gpu_patch import (
    check_metal_support,
    apply_metal_patch,
    build_llama_cpp_metal,
    get_metal_status,
    main
)


class TestMetalSupport:
    """Test Metal support detection."""
    
    def test_non_macos(self):
        """Test Metal not available on non-macOS."""
        with patch('metal_gpu_patch.platform.system', return_value='Linux'):
            result = check_metal_support()
            assert result['supported'] == False
            assert 'Metal only available on macOS' in result['reason']
    
    def test_macos_with_discrete_gpu(self):
        """Test Metal detection with discrete AMD GPU."""
        mock_output = """
Display Type: AMD Radeon Pro 5500M
Total Number of Cores: 8
VRAM: 8 GB
"""
        with patch('metal_gpu_patch.platform.system', return_value='Darwin'), \
             patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout=mock_output)
            result = check_metal_support()
            assert result['supported'] == True
            assert result['is_discrete'] == True
            assert result['is_unified'] == False
    
    def test_macos_with_unified_gpu(self):
        """Test Metal detection with Apple Silicon."""
        mock_output = """
Display Type: Apple M1
Total Number of Cores: 8
"""
        with patch('metal_gpu_patch.platform.system', return_value='Darwin'), \
             patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout=mock_output)
            result = check_metal_support()
            assert result['supported'] == True
            assert result['is_discrete'] == False
            assert result['is_unified'] == True
    
    def test_system_profiler_failure(self):
        """Test handling of system_profiler failure."""
        with patch('metal_gpu_patch.platform.system', return_value='Darwin'), \
             patch('subprocess.run', side_effect=Exception('Command failed')):
            result = check_metal_support()
            assert result['supported'] == False
            assert 'Command failed' in result['reason']


class TestMetalPatch:
    """Test Metal patch application."""
    
    def test_patch_file_not_found(self, tmp_path):
        """Test patch fails when file not found."""
        result = apply_metal_patch(tmp_path / "nonexistent")
        assert result == False
    
    def test_patch_already_applied(self, tmp_path):
        """Test patch detection when already applied."""
        patch_file = tmp_path / "ggml-metal.m"
        patch_file.write_text("StorageModeManaged")
        
        result = apply_metal_patch(tmp_path)
        assert result == True
    
    def test_patch_application(self, tmp_path):
        """Test successful patch application."""
        patch_file = tmp_path / "ggml-metal.m"
        patch_file.write_text("// Original Metal code")
        
        result = apply_metal_patch(tmp_path)
        assert result == True
        
        # Verify patch was applied
        content = patch_file.read_text()
        assert "StorageModeManaged" in content
        assert "is_discrete_gpu" in content


class TestBuildLlamaCpp:
    """Test llama.cpp build process."""
    
    def test_build_success(self, tmp_path):
        """Test successful build."""
        llama_cpp_path = tmp_path / "llama.cpp"
        llama_cpp_path.mkdir()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = build_llama_cpp_metal(llama_cpp_path, tmp_path / "output")
            assert result == True
    
    def test_build_failure(self, tmp_path):
        """Test build failure handling."""
        llama_cpp_path = tmp_path / "llama.cpp"
        llama_cpp_path.mkdir()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="Build error")
            result = build_llama_cpp_metal(llama_cpp_path, tmp_path / "output")
            assert result == False
    
    def test_build_timeout(self, tmp_path):
        """Test build timeout handling."""
        import subprocess
        llama_cpp_path = tmp_path / "llama.cpp"
        llama_cpp_path.mkdir()
        
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd='make', timeout=300)):
            result = build_llama_cpp_metal(llama_cpp_path, tmp_path / "output")
            assert result == False


class TestMetalStatus:
    """Test Metal status reporting."""
    
    def test_status_non_macos(self):
        """Test status on non-macOS."""
        with patch('metal_gpu_patch.platform.system', return_value='Linux'):
            status = get_metal_status()
            assert status['metal_available'] == False
            assert status['gpu_type'] == 'unknown'
    
    def test_status_discrete_amd(self):
        """Test status for discrete AMD GPU."""
        mock_output = "AMD Radeon Pro 5500M"
        
        with patch('metal_gpu_patch.platform.system', return_value='Darwin'), \
             patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout=mock_output)
            status = get_metal_status()
            assert status['metal_available'] == True
            assert status['gpu_type'] == 'discrete_amd'
            assert status['memory_mode'] == 'StorageModeManaged'
    
    def test_status_apple_silicon(self):
        """Test status for Apple Silicon."""
        mock_output = "Apple M1"
        
        with patch('metal_gpu_patch.platform.system', return_value='Darwin'), \
             patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout=mock_output)
            status = get_metal_status()
            assert status['metal_available'] == True
            assert status['gpu_type'] == 'apple_silicon'
            assert status['memory_mode'] == 'StorageModePrivate'


class TestMainFunction:
    """Test main entry point."""
    
    def test_main_non_macos(self):
        """Test main exits on non-macOS."""
        with patch('metal_gpu_patch.platform.system', return_value='Linux'):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
    
    def test_main_macos_success(self, capsys):
        """Test main succeeds on macOS."""
        mock_output = "Apple M1"
        
        with patch('metal_gpu_patch.platform.system', return_value='Darwin'), \
             patch('subprocess.run') as mock_run, \
             patch('sys.exit') as mock_exit:
            mock_run.return_value = MagicMock(stdout=mock_output)
            main()
            captured = capsys.readouterr()
            assert "Metal GPU acceleration setup complete" in captured.out


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
