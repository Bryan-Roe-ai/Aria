#!/usr/bin/env python3
"""
Automatic File Organization System
Organizes datasets, logs, reports, and outputs into proper directory structure
"""

import os
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileOrganizer:
    """Automatically organizes files in the workspace"""
    
    def __init__(self, workspace_root: str = "/workspaces/AI"):
        self.root = Path(workspace_root)
        self.stats = {
            "started_at": datetime.now().isoformat(),
            "files_moved": 0,
            "files_archived": 0,
            "files_deleted": 0,
            "space_freed_mb": 0,
            "operations": []
        }
        
        # Define organization rules
        self.rules = {
            # Datasets organization
            "datasets": {
                "quantum": ["*.csv"],
                "chat": ["*.jsonl", "*.json"],
                "vision": ["*.png", "*.jpg", "*.jpeg"],
                "raw": ["*.raw", "*.dat"]
            },
            
            # Logs organization
            "logs": {
                "training": ["*train*.log", "*lora*.log", "*autotrain*.log"],
                "collection": ["*collection*.log", "*collector*.log", "*download*.log"],
                "error": ["*error*.log", "*fail*.log"],
                "system": ["*system*.log", "*monitor*.log"]
            },
            
            # Reports organization
            "reports": {
                "daily": [],
                "weekly": [],
                "monthly": []
            },
            
            # Model outputs
            "models": {
                "checkpoints": ["checkpoint-*"],
                "final": ["final_*", "best_*"],
                "temp": ["temp_*", "tmp_*"]
            }
        }
    
    def organize_datasets(self):
        """Organize dataset files into proper categories"""
        logger.info("📦 Organizing datasets...")
        
        datasets_dir = self.root / "datasets"
        if not datasets_dir.exists():
            return
        
        organized = 0
        
        # Find misplaced CSV files in root
        for csv_file in datasets_dir.glob("*.csv"):
            # Determine category by content or filename
            target_dir = datasets_dir / "quantum"
            target_dir.mkdir(exist_ok=True)
            
            target_path = target_dir / csv_file.name
            if not target_path.exists():
                shutil.move(str(csv_file), str(target_path))
                organized += 1
                self.stats["files_moved"] += 1
                logger.info(f"  Moved: {csv_file.name} → quantum/")
        
        # Find misplaced JSONL files
        for jsonl_file in datasets_dir.glob("*.jsonl"):
            target_dir = datasets_dir / "chat"
            target_dir.mkdir(exist_ok=True)
            
            target_path = target_dir / jsonl_file.name
            if not target_path.exists():
                shutil.move(str(jsonl_file), str(target_path))
                organized += 1
                self.stats["files_moved"] += 1
                logger.info(f"  Moved: {jsonl_file.name} → chat/")
        
        logger.info(f"  ✅ Organized {organized} dataset files")
        return organized
    
    def organize_logs(self):
        """Organize log files by type and date"""
        logger.info("📝 Organizing logs...")
        
        log_dirs = [
            self.root / "data_out" / "logs",
            self.root / "data_out",
            self.root
        ]
        
        organized = 0
        
        for log_dir in log_dirs:
            if not log_dir.exists():
                continue
            
            for log_file in log_dir.glob("*.log"):
                # Skip if already in organized structure
                if "logs" in str(log_file.parent) and log_file.parent != log_dir:
                    continue
                
                # Determine log type
                log_type = self._classify_log(log_file.name)
                
                # Create target directory structure with date
                file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
                target_dir = self.root / "data_out" / "logs" / log_type / file_date.strftime("%Y-%m")
                target_dir.mkdir(parents=True, exist_ok=True)
                
                target_path = target_dir / log_file.name
                if not target_path.exists() and log_file != target_path:
                    try:
                        shutil.move(str(log_file), str(target_path))
                        organized += 1
                        self.stats["files_moved"] += 1
                        logger.info(f"  Moved: {log_file.name} → logs/{log_type}/{file_date.strftime('%Y-%m')}/")
                    except Exception as e:
                        logger.warning(f"  Failed to move {log_file.name}: {e}")
        
        logger.info(f"  ✅ Organized {organized} log files")
        return organized
    
    def organize_reports(self):
        """Organize report files by type and date"""
        logger.info("📊 Organizing reports...")
        
        report_patterns = ["*_report.json", "*_status.json", "*_results.json", "*_metrics.json"]
        organized = 0
        
        for pattern in report_patterns:
            for report_file in self.root.rglob(pattern):
                # Skip if already organized
                if "reports" in str(report_file.parent):
                    continue
                
                # Determine report age
                file_date = datetime.fromtimestamp(report_file.stat().st_mtime)
                age_days = (datetime.now() - file_date).days
                
                if age_days < 7:
                    period = "daily"
                elif age_days < 30:
                    period = "weekly"
                else:
                    period = "monthly"
                
                # Create target directory
                target_dir = self.root / "data_out" / "reports" / period / file_date.strftime("%Y-%m")
                target_dir.mkdir(parents=True, exist_ok=True)
                
                target_path = target_dir / report_file.name
                if not target_path.exists():
                    try:
                        shutil.copy2(str(report_file), str(target_path))
                        organized += 1
                        self.stats["files_moved"] += 1
                        logger.info(f"  Copied: {report_file.name} → reports/{period}/")
                    except Exception as e:
                        logger.warning(f"  Failed to copy {report_file.name}: {e}")
        
        logger.info(f"  ✅ Organized {organized} report files")
        return organized
    
    def archive_old_files(self, days_threshold: int = 30):
        """Archive files older than threshold"""
        logger.info(f"📦 Archiving files older than {days_threshold} days...")
        
        archive_dir = self.root / "archive" / datetime.now().strftime("%Y-%m")
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        archived = 0
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        # Archive old logs
        log_dir = self.root / "data_out" / "logs"
        if log_dir.exists():
            for log_file in log_dir.rglob("*.log"):
                file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_date < cutoff_date:
                    relative_path = log_file.relative_to(log_dir)
                    target_path = archive_dir / "logs" / relative_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        shutil.move(str(log_file), str(target_path))
                        archived += 1
                        self.stats["files_archived"] += 1
                    except Exception as e:
                        logger.warning(f"  Failed to archive {log_file.name}: {e}")
        
        logger.info(f"  ✅ Archived {archived} old files")
        return archived
    
    def cleanup_temp_files(self):
        """Remove temporary and duplicate files"""
        logger.info("🧹 Cleaning up temporary files...")
        
        temp_patterns = [
            "*.tmp",
            "*.temp",
            "*~",
            "*.swp",
            "*.swo",
            ".DS_Store",
            "Thumbs.db",
            "__pycache__"
        ]
        
        cleaned = 0
        space_freed = 0
        
        for pattern in temp_patterns:
            for temp_file in self.root.rglob(pattern):
                try:
                    if temp_file.is_dir():
                        space_freed += sum(f.stat().st_size for f in temp_file.rglob('*') if f.is_file())
                        shutil.rmtree(temp_file)
                    else:
                        space_freed += temp_file.stat().st_size
                        temp_file.unlink()
                    
                    cleaned += 1
                    self.stats["files_deleted"] += 1
                    logger.info(f"  Deleted: {temp_file.name}")
                except Exception as e:
                    logger.warning(f"  Failed to delete {temp_file}: {e}")
        
        self.stats["space_freed_mb"] = space_freed / 1024 / 1024
        logger.info(f"  ✅ Cleaned {cleaned} temp files ({space_freed/1024/1024:.1f} MB freed)")
        return cleaned
    
    def remove_duplicates(self):
        """Find and remove duplicate files"""
        logger.info("🔍 Finding duplicate files...")
        
        # Build hash map
        hash_map = {}
        duplicates = []
        
        # Check datasets for duplicates
        datasets_dir = self.root / "datasets"
        if datasets_dir.exists():
            for file_path in datasets_dir.rglob("*.csv"):
                if file_path.stat().st_size == 0:
                    continue
                
                file_hash = self._get_file_hash(file_path)
                if file_hash in hash_map:
                    duplicates.append((file_path, hash_map[file_hash]))
                else:
                    hash_map[file_hash] = file_path
        
        # Remove duplicates (keep original, remove copies)
        removed = 0
        for dup, original in duplicates:
            try:
                logger.info(f"  Duplicate: {dup.name} == {original.name}")
                dup.unlink()
                removed += 1
                self.stats["files_deleted"] += 1
            except Exception as e:
                logger.warning(f"  Failed to remove duplicate {dup}: {e}")
        
        logger.info(f"  ✅ Removed {removed} duplicate files")
        return removed
    
    def organize_model_outputs(self):
        """Organize model checkpoints and outputs"""
        logger.info("🤖 Organizing model outputs...")
        
        organized = 0
        
        # Find model outputs in data_out
        data_out = self.root / "data_out"
        if not data_out.exists():
            return 0
        
        # Organize checkpoints
        for checkpoint_dir in data_out.rglob("checkpoint-*"):
            if not checkpoint_dir.is_dir():
                continue
            
            # Move to organized structure
            target_dir = self.root / "deployed_models" / "checkpoints" / checkpoint_dir.parent.name
            target_dir.mkdir(parents=True, exist_ok=True)
            
            target_path = target_dir / checkpoint_dir.name
            if not target_path.exists():
                try:
                    shutil.move(str(checkpoint_dir), str(target_path))
                    organized += 1
                    self.stats["files_moved"] += 1
                    logger.info(f"  Moved: {checkpoint_dir.name} → deployed_models/checkpoints/")
                except Exception as e:
                    logger.warning(f"  Failed to move {checkpoint_dir}: {e}")
        
        logger.info(f"  ✅ Organized {organized} model outputs")
        return organized
    
    def create_index(self):
        """Create an index of organized files"""
        logger.info("📇 Creating file index...")
        
        index = {
            "created_at": datetime.now().isoformat(),
            "datasets": {},
            "logs": {},
            "reports": {},
            "models": {}
        }
        
        # Index datasets
        datasets_dir = self.root / "datasets"
        if datasets_dir.exists():
            for category in ["quantum", "chat", "vision", "massive_quantum"]:
                cat_dir = datasets_dir / category
                if cat_dir.exists():
                    index["datasets"][category] = {
                        "count": len(list(cat_dir.rglob("*.*"))),
                        "size_mb": sum(f.stat().st_size for f in cat_dir.rglob("*") if f.is_file()) / 1024 / 1024
                    }
        
        # Index logs
        log_dir = self.root / "data_out" / "logs"
        if log_dir.exists():
            for log_type in ["training", "collection", "error", "system"]:
                type_dir = log_dir / log_type
                if type_dir.exists():
                    index["logs"][log_type] = {
                        "count": len(list(type_dir.rglob("*.log"))),
                        "size_mb": sum(f.stat().st_size for f in type_dir.rglob("*.log")) / 1024 / 1024
                    }
        
        # Save index
        index_file = self.root / "data_out" / "file_organization_index.json"
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        logger.info(f"  ✅ Index created: {index_file}")
        return index
    
    def _classify_log(self, filename: str) -> str:
        """Classify log file by name"""
        filename_lower = filename.lower()
        
        if any(x in filename_lower for x in ["train", "lora", "autotrain", "model"]):
            return "training"
        elif any(x in filename_lower for x in ["collect", "download", "dataset"]):
            return "collection"
        elif any(x in filename_lower for x in ["error", "fail", "exception"]):
            return "error"
        else:
            return "system"
    
    def _get_file_hash(self, file_path: Path, block_size: int = 65536) -> str:
        """Calculate SHA256 hash of file"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()
    
    def generate_report(self):
        """Generate organization report"""
        self.stats["completed_at"] = datetime.now().isoformat()
        
        report_dir = self.root / "data_out" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"organization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        return report_file
    
    def run_full_organization(self, archive_days: int = 30, remove_duplicates: bool = True):
        """Run complete organization process"""
        logger.info("="*80)
        logger.info("🚀 AUTOMATED FILE ORGANIZATION")
        logger.info("="*80)
        
        try:
            # Run all organization tasks
            self.organize_datasets()
            self.organize_logs()
            self.organize_reports()
            self.organize_model_outputs()
            self.cleanup_temp_files()
            
            if archive_days > 0:
                self.archive_old_files(archive_days)
            
            if remove_duplicates:
                self.remove_duplicates()
            
            # Create index
            index = self.create_index()
            
            # Generate report
            report_file = self.generate_report()
            
            logger.info("\n" + "="*80)
            logger.info("✅ ORGANIZATION COMPLETE!")
            logger.info("="*80)
            logger.info(f"Files moved: {self.stats['files_moved']}")
            logger.info(f"Files archived: {self.stats['files_archived']}")
            logger.info(f"Files deleted: {self.stats['files_deleted']}")
            logger.info(f"Space freed: {self.stats['space_freed_mb']:.1f} MB")
            logger.info(f"Report: {report_file}")
            logger.info("="*80)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Organization failed: {e}", exc_info=True)
            return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated File Organization")
    parser.add_argument("--archive-days", type=int, default=30,
                       help="Archive files older than N days (0 to disable)")
    parser.add_argument("--no-duplicates", action="store_true",
                       help="Skip duplicate removal")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    organizer = FileOrganizer()
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No changes will be made")
    
    success = organizer.run_full_organization(
        archive_days=args.archive_days,
        remove_duplicates=not args.no_duplicates
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
