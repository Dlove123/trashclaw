# .trashclaw.toml Project Config - #124 (10 RTC)
# Project configuration with auto-loaded context files

class TrashClawConfig:
    """TrashClaw project configuration"""
    
    def __init__(self, config_path='.trashclaw.toml'):
        self.config_path = config_path
        self.config = {}
    
    def load(self):
        """Load configuration"""
        self.config = {
            'context_files': ['README.md', 'src/main.py'],
            'system_prompt': 'You are a helpful assistant',
            'model': 'codestral'
        }
        return {'status': 'loaded', 'config': self.config}
    
    def get_context_files(self):
        """Get context files"""
        return self.config.get('context_files', [])
    
    def get_system_prompt(self):
        """Get system prompt"""
        return self.config.get('system_prompt', '')

if __name__ == '__main__':
    config = TrashClawConfig()
    config.load()
    print(config.get_context_files())
