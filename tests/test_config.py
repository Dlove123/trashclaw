"""
Tests for .trashclaw.toml configuration
"""

import os
import toml
import pytest

CONFIG_PATH = ".trashclaw.toml"


class TestTrashclawConfig:
    """Test suite for TrashClaw configuration"""
    
    def test_config_file_exists(self):
        """Test that config file exists"""
        assert os.path.exists(CONFIG_PATH), f"Config file {CONFIG_PATH} not found"
    
    def test_config_is_valid_toml(self):
        """Test that config is valid TOML"""
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        assert isinstance(config, dict)
    
    def test_agent_section(self):
        """Test agent section exists"""
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        assert 'agent' in config
        assert 'name' in config['agent']
        assert config['agent']['name'] == 'TrashClaw'
    
    def test_server_section(self):
        """Test server section exists"""
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        assert 'server' in config
        assert 'host' in config['server']
        assert 'port' in config['server']
    
    def test_model_section(self):
        """Test model section exists"""
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        assert 'model' in config
        assert 'context_length' in config['model']
    
    def test_tools_section(self):
        """Test tools section exists"""
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        assert 'tools' in config
        assert 'file_tools' in config['tools']
        assert 'shell_tools' in config['tools']
    
    def test_context_section(self):
        """Test context section exists"""
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        assert 'context' in config
        assert 'auto_load' in config['context']
    
    def test_ui_section(self):
        """Test UI section exists"""
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        assert 'ui' in config
        assert 'theme' in config['ui']
    
    def test_logging_section(self):
        """Test logging section exists"""
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        assert 'logging' in config
        assert 'level' in config['logging']
    
    def test_security_section(self):
        """Test security section exists"""
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        assert 'security' in config
        assert 'allowed_directories' in config['security']
        assert 'blocked_commands' in config['security']
    
    def test_security_blocked_commands(self):
        """Test dangerous commands are blocked"""
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        blocked = config['security']['blocked_commands']
        assert 'rm -rf /' in blocked
        assert 'mkfs' in blocked
    
    def test_context_auto_load(self):
        """Test context auto-load is enabled"""
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        assert config['context']['auto_load'] == True
    
    def test_confirm_commands_enabled(self):
        """Test command confirmation is enabled for safety"""
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        assert config['ui']['confirm_commands'] == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
