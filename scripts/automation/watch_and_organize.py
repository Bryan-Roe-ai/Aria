#!/usr/bin/env python3
"""
Real-time File Watcher and Organizer
Monitors directories and automatically organizes new files
"""

import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys

sys.path.insert(0, str(Path(__file__).parent))
from auto_organize import FileOrganizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileOrganizerHandler(FileSystemEventHandler):
    """Handles file system events and organizes files"""
    
    def __init__(self, organizer: FileOrganizer):
        self.organizer = organizer
        self.last_run = time.time()
        self.cooldown = 60  # Don't organize more than once per minute
    
    def on_created(self, event):
        """Called when a file is created"""
        if event.is_directory:
            return
        
        # Check cooldown
        if time.time() - self.last_run < self.cooldown:
            return
        
        file_path = Path(event.src_path)
        logger.info(f"📁 New file detected: {file_path.name}")
        
        # Organize based on file type
        if file_path.suffix == ".log":
            self.organizer.organize_logs()
        elif file_path.suffix in [".csv", ".jsonl"]:
            self.organizer.organize_datasets()
        elif file_path.suffix == ".json" and "report" in file_path.name:
            self.organizer.organize_reports()
        
        self.last_run = time.time()
    
    def on_modified(self, event):
        """Called when a file is modified"""
        # Only organize on creation, not modification
        pass


def main():
    """Main watcher"""
    workspace = Path("/workspaces/AI")
    
    logger.info("="*80)
    logger.info("👁️  REAL-TIME FILE ORGANIZATION WATCHER")
    logger.info("="*80)
    logger.info(f"Watching: {workspace}")
    logger.info("Press Ctrl+C to stop")
    logger.info("="*80)
    
    organizer = FileOrganizer()
    event_handler = FileOrganizerHandler(organizer)
    observer = Observer()
    
    # Watch key directories
    watch_dirs = [
        workspace / "datasets",
        workspace / "data_out",
        workspace / "data_out" / "logs"
    ]
    
    for watch_dir in watch_dirs:
        if watch_dir.exists():
            observer.schedule(event_handler, str(watch_dir), recursive=True)
            logger.info(f"  Watching: {watch_dir}")
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("\n⏹️  Watcher stopped")
    
    observer.join()


if __name__ == "__main__":
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        main()
    except ImportError:
        logger.error("❌ watchdog not installed. Install with: pip install watchdog")
        logger.info("   Running one-time organization instead...")
        organizer = FileOrganizer()
        organizer.run_full_organization()
