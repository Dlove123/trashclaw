#!/usr/bin/env python3
"""
Token-per-second display and generation stats
Bounty #64 - 10 RTC

Show generation speed stats after each agent turn.
"""

import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerationStats:
    """Statistics for a single generation."""
    tokens: int = 0
    elapsed_time: float = 0.0
    tokens_per_second: float = 0.0
    
    def __str__(self):
        return f"[{self.tokens_per_second:.1f} tok/s | {self.tokens} tokens | {self.elapsed_time:.1f}s]"


@dataclass 
class SessionStats:
    """Cumulative session statistics."""
    total_tokens: int = 0
    total_time: float = 0.0
    total_generations: int = 0
    
    @property
    def avg_tokens_per_second(self) -> float:
        if self.total_time == 0:
            return 0.0
        return self.total_tokens / self.total_time
    
    def __str__(self):
        return (f"Session Stats:\n"
                f"  Total tokens: {self.total_tokens}\n"
                f"  Total time: {self.total_time:.1f}s\n"
                f"  Generations: {self.total_generations}\n"
                f"  Average speed: {self.avg_tokens_per_second:.1f} tok/s")


class TokenCounter:
    """Count tokens during streaming generation."""
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.token_count: int = 0
        self.last_stats: Optional[GenerationStats] = None
        self.session_stats: SessionStats = SessionStats()
    
    def start(self):
        """Start timing generation."""
        self.start_time = time.time()
        self.token_count = 0
        self.end_time = None
    
    def count_chunk(self, chunk: str):
        """
        Count tokens in a chunk during streaming.
        
        Args:
            chunk: Text chunk from streaming response
        """
        # Simple token counting: ~4 chars per token (approximation)
        # For more accurate counting, use tiktoken or similar
        tokens_in_chunk = len(chunk) // 4
        self.token_count += tokens_in_chunk
    
    def end(self) -> GenerationStats:
        """
        End generation and calculate stats.
        
        Returns:
            GenerationStats object
        """
        self.end_time = time.time()
        
        if self.start_time is None:
            raise RuntimeError("Generation not started")
        
        elapsed = self.end_time - self.start_time
        
        # Avoid division by zero
        if elapsed > 0:
            tokens_per_second = self.token_count / elapsed
        else:
            tokens_per_second = 0.0
        
        stats = GenerationStats(
            tokens=self.token_count,
            elapsed_time=elapsed,
            tokens_per_second=tokens_per_second
        )
        
        self.last_stats = stats
        
        # Update session stats
        self.session_stats.total_tokens += self.token_count
        self.session_stats.total_time += elapsed
        self.session_stats.total_generations += 1
        
        return stats
    
    def get_stats_display(self) -> str:
        """
        Get formatted stats display string.
        
        Returns:
            Formatted stats string
        """
        if self.last_stats:
            return str(self.last_stats)
        return "[No stats available]"
    
    def get_session_display(self) -> str:
        """
        Get formatted session stats display string.
        
        Returns:
            Formatted session stats string
        """
        return str(self.session_stats)
    
    def reset_session(self):
        """Reset session statistics."""
        self.session_stats = SessionStats()
        self.last_stats = None
        self.token_count = 0
        self.start_time = None
        self.end_time = None


# Global token counter instance
_global_counter: Optional[TokenCounter] = None


def get_token_counter() -> TokenCounter:
    """Get or create global token counter."""
    global _global_counter
    if _global_counter is None:
        _global_counter = TokenCounter()
    return _global_counter


def start_generation():
    """Start tracking a new generation."""
    counter = get_token_counter()
    counter.start()


def count_tokens(chunk: str):
    """Count tokens in a streaming chunk."""
    counter = get_token_counter()
    counter.count_chunk(chunk)


def end_generation() -> str:
    """
    End generation and return stats display.
    
    Returns:
        Formatted stats string
    """
    counter = get_token_counter()
    stats = counter.end()
    return str(stats)


def get_status() -> dict:
    """
    Get current token stats for /status command.
    
    Returns:
        Dict with token stats
    """
    counter = get_token_counter()
    
    result = {
        "token_stats": {
            "last_generation": None,
            "session": {
                "total_tokens": counter.session_stats.total_tokens,
                "total_time": round(counter.session_stats.total_time, 1),
                "total_generations": counter.session_stats.total_generations,
                "avg_tokens_per_second": round(counter.session_stats.avg_tokens_per_second, 1)
            }
        }
    }
    
    if counter.last_stats:
        result["token_stats"]["last_generation"] = {
            "tokens": counter.last_stats.tokens,
            "elapsed_time": round(counter.last_stats.elapsed_time, 1),
            "tokens_per_second": round(counter.last_stats.tokens_per_second, 1)
        }
    
    return result


def reset_stats():
    """Reset all token statistics."""
    counter = get_token_counter()
    counter.reset_session()


if __name__ == "__main__":
    # Demo/test
    print("=== Token Stats Demo ===\n")
    
    # Simulate 3 generations
    for i in range(3):
        print(f"Generation {i+1}:")
        start_generation()
        
        # Simulate streaming chunks
        for chunk in ["Hello ", "world ", "this ", "is ", "a ", "test "] * 10:
            count_tokens(chunk)
            time.sleep(0.01)  # Simulate streaming delay
        
        stats = end_generation()
        print(f"  {stats}\n")
    
    # Show session stats
    print(get_status())
