"""
Performance Utilities

Common performance-optimized patterns for the Aria codebase.
Provides reusable functions that follow best practices.
"""

from collections import deque
from pathlib import Path
from typing import List, Iterator, Optional, Callable, Any
import json


def tail_file(file_path: Path, max_lines: int = 20) -> List[str]:
    """
    Memory-efficient tail operation for log files.
    
    Uses collections.deque to keep only the last N lines in memory,
    instead of loading the entire file.
    
    Args:
        file_path: Path to the file to read
        max_lines: Number of lines to return from the end
        
    Returns:
        List of the last max_lines from the file
        
    Example:
        >>> logs = tail_file(Path("data_out/training.log"), max_lines=50)
        >>> for log in logs:
        ...     print(log.strip())
    """
    if not file_path.exists():
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return list(deque(f, maxlen=max_lines))
    except Exception:
        return []


def tail_file_smart(file_path: Path, max_lines: int = 20, 
                    small_file_threshold: int = 65536) -> List[str]:
    """
    Smart tail operation that adapts to file size.
    
    For small files (< threshold), reads entire file.
    For large files, reads backwards in blocks for efficiency.
    
    Args:
        file_path: Path to the file to read
        max_lines: Number of lines to return from the end
        small_file_threshold: Size in bytes below which to use simple read
        
    Returns:
        List of the last max_lines from the file
    """
    if not file_path.exists():
        return []
    
    try:
        size = file_path.stat().st_size
        
        # Small file: simple read
        if size <= small_file_threshold:
            with file_path.open("r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                return lines[-max_lines:]
        
        # Large file: read backwards in blocks
        block_size = 8192
        with file_path.open("rb") as f:
            pos = max(0, size - block_size)
            f.seek(pos)
            buf = f.read(block_size)
            
            while True:
                decoded = buf.decode("utf-8", errors="ignore")
                lines = decoded.splitlines()
                
                if len(lines) >= max_lines or pos == 0:
                    return lines[-max_lines:]
                
                # Move further back
                new_pos = max(0, pos - block_size)
                read_size = pos - new_pos
                f.seek(new_pos)
                more = f.read(read_size)
                buf = more + buf
                pos = new_pos
    except Exception:
        return []


def stream_jsonl(file_path: Path, 
                 filter_fn: Optional[Callable[[dict], bool]] = None) -> Iterator[dict]:
    """
    Memory-efficient streaming of JSONL files.
    
    Yields one JSON object at a time instead of loading the entire file.
    
    Args:
        file_path: Path to JSONL file
        filter_fn: Optional function to filter records (return True to include)
        
    Yields:
        Parsed JSON objects from the file
        
    Example:
        >>> for record in stream_jsonl(Path("dataset.jsonl")):
        ...     process(record)
        
        >>> # With filtering
        >>> valid_records = stream_jsonl(
        ...     Path("dataset.jsonl"),
        ...     filter_fn=lambda r: r.get('valid', False)
        ... )
        >>> for record in valid_records:
        ...     process(record)
    """
    if not file_path.exists():
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                obj = json.loads(line)
                if filter_fn is None or filter_fn(obj):
                    yield obj
            except json.JSONDecodeError:
                continue


def batch_process(items: List[Any], batch_size: int, 
                  process_fn: Callable[[List[Any]], None]) -> None:
    """
    Process items in batches to reduce memory pressure.
    
    Args:
        items: List of items to process
        batch_size: Number of items per batch
        process_fn: Function that takes a batch of items
        
    Example:
        >>> def save_batch(batch):
        ...     with open('output.json', 'a') as f:
        ...         for item in batch:
        ...             f.write(json.dumps(item) + '\\n')
        >>> 
        >>> large_dataset = load_data()
        >>> batch_process(large_dataset, batch_size=100, process_fn=save_batch)
    """
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        process_fn(batch)


def find_json_in_output(output: str, key: Optional[str] = None, 
                       search_from_end: bool = True, max_lines: int = 50) -> Optional[dict]:
    """
    Efficiently find JSON object in command output.
    
    Searches from the end by default since metrics/results are typically
    at the bottom of the output.
    
    Args:
        output: String output to search
        key: Optional key that must be present in the JSON object
        search_from_end: If True, search from the end of output
        max_lines: Maximum number of lines to search
        
    Returns:
        First matching JSON object, or None if not found
        
    Example:
        >>> output = subprocess.run(['./script.sh'], capture_output=True, text=True)
        >>> metrics = find_json_in_output(output.stdout, key='metrics')
        >>> if metrics:
        ...     print(f"Accuracy: {metrics['metrics']['accuracy']}")
    """
    # Split and optionally reverse for end-first search
    lines = output.rsplit('\n', max_lines) if search_from_end else output.split('\n', max_lines)
    line_iter = reversed(lines) if search_from_end else lines
    
    for line in line_iter:
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                obj = json.loads(line)
                if key is None or key in obj:
                    return obj
            except json.JSONDecodeError:
                continue
    
    return None


class FileCache:
    """
    Simple in-memory cache for file contents with size limits.
    
    Use for files that are read multiple times but don't change often.
    
    Example:
        >>> cache = FileCache(max_size_mb=10)
        >>> 
        >>> # First read - from disk
        >>> data1 = cache.read(Path('config.yaml'))
        >>> 
        >>> # Second read - from cache (fast)
        >>> data2 = cache.read(Path('config.yaml'))
        >>> 
        >>> # Clear cache if needed
        >>> cache.clear()
    """
    
    def __init__(self, max_size_mb: float = 10.0):
        self._cache: dict[Path, bytes] = {}
        self._sizes: dict[Path, int] = {}
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.current_size = 0
    
    def read(self, file_path: Path, encoding: str = 'utf-8') -> str:
        """Read file from cache or disk."""
        if file_path in self._cache:
            return self._cache[file_path].decode(encoding)
        
        # Read from disk
        data = file_path.read_bytes()
        size = len(data)
        
        # Only cache if it fits
        if self.current_size + size <= self.max_size_bytes:
            self._cache[file_path] = data
            self._sizes[file_path] = size
            self.current_size += size
        
        return data.decode(encoding)
    
    def read_bytes(self, file_path: Path) -> bytes:
        """Read file bytes from cache or disk."""
        if file_path in self._cache:
            return self._cache[file_path]
        
        data = file_path.read_bytes()
        size = len(data)
        
        if self.current_size + size <= self.max_size_bytes:
            self._cache[file_path] = data
            self._sizes[file_path] = size
            self.current_size += size
        
        return data
    
    def invalidate(self, file_path: Path) -> None:
        """Remove a file from cache."""
        if file_path in self._cache:
            size = self._sizes[file_path]
            del self._cache[file_path]
            del self._sizes[file_path]
            self.current_size -= size
    
    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
        self._sizes.clear()
        self.current_size = 0
    
    def stats(self) -> dict:
        """Get cache statistics."""
        return {
            'entries': len(self._cache),
            'current_size_mb': self.current_size / (1024 * 1024),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'utilization': (self.current_size / self.max_size_bytes) * 100 if self.max_size_bytes > 0 else 0
        }


# Example usage and tests
if __name__ == "__main__":
    import tempfile
    import sys
    
    print("Performance Utilities - Example Usage\n")
    
    # Test tail_file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        temp_path = Path(f.name)
        for i in range(100):
            f.write(f"Log line {i}\n")
    
    print("1. tail_file() - Last 5 lines:")
    lines = tail_file(temp_path, max_lines=5)
    for line in lines:
        print(f"  {line.strip()}")
    
    # Test stream_jsonl
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        temp_jsonl = Path(f.name)
        for i in range(10):
            f.write(json.dumps({'id': i, 'valid': i % 2 == 0}) + '\n')
    
    print("\n2. stream_jsonl() - Valid records only:")
    for obj in stream_jsonl(temp_jsonl, filter_fn=lambda x: x.get('valid')):
        print(f"  ID: {obj['id']}")
    
    # Test find_json_in_output
    output = """
    Starting process...
    Processing data...
    {"metrics": {"accuracy": 0.95, "loss": 0.05}}
    Complete.
    """
    
    print("\n3. find_json_in_output() - Extract metrics:")
    metrics = find_json_in_output(output, key='metrics')
    if metrics:
        print(f"  Found: {metrics}")
    
    # Test FileCache
    print("\n4. FileCache() - Caching demo:")
    cache = FileCache(max_size_mb=1)
    
    # First read
    import time
    t0 = time.time()
    content1 = cache.read(temp_path)
    t1 = time.time() - t0
    print(f"  First read (disk): {t1*1000:.2f}ms")
    
    # Second read
    t0 = time.time()
    content2 = cache.read(temp_path)
    t2 = time.time() - t0
    print(f"  Second read (cache): {t2*1000:.2f}ms")
    print(f"  Speedup: {t1/t2:.1f}x")
    print(f"  Cache stats: {cache.stats()}")
    
    # Cleanup
    temp_path.unlink()
    temp_jsonl.unlink()
    
    print("\n✅ All examples completed successfully!")
