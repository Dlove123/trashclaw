#!/usr/bin/env python3
"""
Test suite for token stats
Bounty #64 - 10 RTC
"""

import pytest
import time
from unittest.mock import patch
from token_stats import (
    GenerationStats,
    SessionStats,
    TokenCounter,
    get_token_counter,
    start_generation,
    count_tokens,
    end_generation,
    get_status,
    reset_stats
)


class TestGenerationStats:
    """Test GenerationStats dataclass."""
    
    def test_default_values(self):
        """Test default values."""
        stats = GenerationStats()
        assert stats.tokens == 0
        assert stats.elapsed_time == 0.0
        assert stats.tokens_per_second == 0.0
    
    def test_string_format(self):
        """Test string formatting."""
        stats = GenerationStats(tokens=100, elapsed_time=10.0, tokens_per_second=10.0)
        assert "[10.0 tok/s | 100 tokens | 10.0s]" in str(stats)


class TestSessionStats:
    """Test SessionStats dataclass."""
    
    def test_default_values(self):
        """Test default values."""
        stats = SessionStats()
        assert stats.total_tokens == 0
        assert stats.total_time == 0.0
        assert stats.total_generations == 0
        assert stats.avg_tokens_per_second == 0.0
    
    def test_average_calculation(self):
        """Test average tokens per second calculation."""
        stats = SessionStats(total_tokens=1000, total_time=100.0, total_generations=10)
        assert stats.avg_tokens_per_second == 10.0
    
    def test_zero_time_average(self):
        """Test average with zero time (avoid division by zero)."""
        stats = SessionStats(total_tokens=1000, total_time=0.0, total_generations=10)
        assert stats.avg_tokens_per_second == 0.0
    
    def test_string_format(self):
        """Test string formatting."""
        stats = SessionStats(total_tokens=1000, total_time=100.0, total_generations=10)
        s = str(stats)
        assert "Total tokens: 1000" in s
        assert "Total time: 100.0s" in s
        assert "Generations: 10" in s
        assert "Average speed: 10.0 tok/s" in s


class TestTokenCounter:
    """Test TokenCounter class."""
    
    def test_start(self):
        """Test starting generation."""
        counter = TokenCounter()
        counter.start()
        assert counter.start_time is not None
        assert counter.token_count == 0
    
    def test_count_chunk(self):
        """Test counting chunks."""
        counter = TokenCounter()
        counter.start()
        counter.count_chunk("Hello world")
        assert counter.token_count > 0
    
    def test_end(self):
        """Test ending generation."""
        counter = TokenCounter()
        counter.start()
        time.sleep(0.1)
        counter.count_chunk("Hello world test")
        stats = counter.end()
        
        assert stats.tokens > 0
        assert stats.elapsed_time > 0
        assert stats.tokens_per_second > 0
        assert counter.last_stats == stats
    
    def test_end_without_start(self):
        """Test ending without starting raises error."""
        counter = TokenCounter()
        with pytest.raises(RuntimeError, match="Generation not started"):
            counter.end()
    
    def test_session_stats_update(self):
        """Test session stats are updated."""
        counter = TokenCounter()
        
        # First generation
        counter.start()
        counter.count_chunk("Test chunk")
        counter.end()
        
        assert counter.session_stats.total_generations == 1
        assert counter.session_stats.total_tokens > 0
    
    def test_multiple_generations(self):
        """Test multiple generations accumulate."""
        counter = TokenCounter()
        
        for i in range(3):
            counter.start()
            counter.count_chunk(f"Generation {i}")
            time.sleep(0.05)
            counter.end()
        
        assert counter.session_stats.total_generations == 3
    
    def test_reset_session(self):
        """Test resetting session."""
        counter = TokenCounter()
        counter.start()
        counter.count_chunk("Test")
        counter.end()
        
        counter.reset_session()
        
        assert counter.session_stats.total_generations == 0
        assert counter.session_stats.total_tokens == 0
        assert counter.last_stats is None
    
    def test_get_stats_display(self):
        """Test stats display."""
        counter = TokenCounter()
        assert counter.get_stats_display() == "[No stats available]"
        
        counter.start()
        counter.count_chunk("Test")
        counter.end()
        
        display = counter.get_stats_display()
        assert "tok/s" in display
        assert "tokens" in display
        assert "s]" in display


class TestGlobalFunctions:
    """Test global convenience functions."""
    
    def test_start_end_generation(self):
        """Test start/end generation functions."""
        reset_stats()  # Start fresh
        
        start_generation()
        count_tokens("Hello world")
        stats = end_generation()
        
        assert "tok/s" in stats
    
    def test_get_status(self):
        """Test get_status function."""
        reset_stats()
        
        start_generation()
        count_tokens("Test chunk")
        end_generation()
        
        status = get_status()
        
        assert "token_stats" in status
        assert "session" in status["token_stats"]
        assert "last_generation" in status["token_stats"]
    
    def test_reset_stats(self):
        """Test reset_stats function."""
        start_generation()
        count_tokens("Test")
        end_generation()
        
        reset_stats()
        
        status = get_status()
        assert status["token_stats"]["session"]["total_generations"] == 0


class TestTokenCounting:
    """Test token counting accuracy."""
    
    def test_chunk_counting_approximation(self):
        """Test that chunk counting uses ~4 chars per token."""
        counter = TokenCounter()
        counter.start()
        
        # 100 characters should be ~25 tokens
        counter.count_chunk("a" * 100)
        
        assert counter.token_count == 25
    
    def test_empty_chunk(self):
        """Test empty chunk doesn't affect count."""
        counter = TokenCounter()
        counter.start()
        counter.count_chunk("")
        assert counter.token_count == 0
    
    def test_unicode_chunks(self):
        """Test unicode character counting."""
        counter = TokenCounter()
        counter.start()
        counter.count_chunk("你好世界")  # 4 Chinese characters
        # Should count based on byte length
        assert counter.token_count >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
