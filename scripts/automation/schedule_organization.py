#!/usr/bin/env python3
"""
Scheduled File Organization
Runs file organization on a schedule (hourly, daily, weekly)
"""

import time
import schedule
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from auto_organize import FileOrganizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_out/logs/auto_organization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_hourly_organization():
    """Light organization every hour"""
    logger.info("⏰ Running hourly organization...")
    organizer = FileOrganizer()
    organizer.organize_logs()
    organizer.cleanup_temp_files()


def run_daily_organization():
    """Full organization daily"""
    logger.info("📅 Running daily organization...")
    organizer = FileOrganizer()
    organizer.run_full_organization(archive_days=30, remove_duplicates=False)


def run_weekly_organization():
    """Deep organization weekly"""
    logger.info("📆 Running weekly organization...")
    organizer = FileOrganizer()
    organizer.run_full_organization(archive_days=30, remove_duplicates=True)


def main():
    """Main scheduler"""
    logger.info("="*80)
    logger.info("🕐 SCHEDULED FILE ORGANIZATION STARTED")
    logger.info("="*80)
    logger.info("Hourly: Light cleanup (logs, temp files)")
    logger.info("Daily:  Full organization")
    logger.info("Weekly: Deep organization with deduplication")
    logger.info("="*80)
    
    # Schedule tasks
    schedule.every().hour.do(run_hourly_organization)
    schedule.every().day.at("02:00").do(run_daily_organization)
    schedule.every().sunday.at("03:00").do(run_weekly_organization)
    
    # Run initial organization
    run_hourly_organization()
    
    # Run scheduler
    logger.info("⏰ Scheduler running... (Ctrl+C to stop)")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("\n⏹️  Scheduler stopped")


if __name__ == "__main__":
    main()
