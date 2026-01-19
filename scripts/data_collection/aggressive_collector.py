#!/usr/bin/env python3
"""
Aggressive Dataset Collection
Maximizes dataset gathering with parallel processing and all available sources
"""

import asyncio
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from comprehensive_dataset_collector import DatasetCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def aggressive_collection():
    """Collect maximum datasets from all sources"""
    collector = DatasetCollector()
    
    # Configuration for aggressive collection
    sources_config = {
        "sklearn": 50,      # All sklearn datasets
        "uci": 100,         # Many UCI datasets
        "openml": 200,      # Lots of OpenML datasets
    }
    
    logger.info("="*80)
    logger.info("🚀 AGGRESSIVE DATASET COLLECTION MODE")
    logger.info("="*80)
    logger.info(f"Sources: {list(sources_config.keys())}")
    logger.info(f"Total potential: {sum(sources_config.values())} datasets per category")
    logger.info("="*80)
    
    all_datasets = []
    
    # Collect from each source with specific limits
    for source, limit in sources_config.items():
        logger.info(f"\n📦 Collecting from {source.upper()} (limit: {limit})")
        
        for category in collector.categories:
            try:
                collector_func = collector.sources[source]
                datasets = await collector_func(category, limit=limit)
                all_datasets.extend(datasets)
                
                logger.info(f"  ✅ {category}: {len(datasets)} datasets")
                
            except Exception as e:
                logger.error(f"  ❌ Error in {source}/{category}: {e}")
                continue
    
    # Augment everything
    logger.info(f"\n🔄 Augmenting {len(all_datasets)} datasets...")
    aug_count = await collector.augment_datasets(all_datasets)
    
    # Validate everything
    logger.info(f"\n🔍 Validating {len(all_datasets)} datasets...")
    valid, invalid = await collector.validate_datasets(all_datasets)
    
    # Save report
    collector.stats["downloaded"] = len(all_datasets)
    collector.stats["augmented"] = aug_count
    collector.stats["validated"] = valid
    collector.stats["failed"] = invalid
    collector.save_report(all_datasets)
    
    logger.info("\n" + "="*80)
    logger.info("✅ AGGRESSIVE COLLECTION COMPLETE!")
    logger.info(f"   Total Downloaded: {len(all_datasets)}")
    logger.info(f"   Total Augmented: {aug_count}")
    logger.info(f"   Valid: {valid}")
    logger.info(f"   Failed: {invalid}")
    logger.info("="*80)
    
    return all_datasets


if __name__ == "__main__":
    asyncio.run(aggressive_collection())
