#!/usr/bin/env python3
"""
HuggingFace Bulk Dataset Collector
Specifically targets high-quality chat/instruction datasets from HuggingFace
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HuggingFaceBulkCollector:
    """Bulk collection from HuggingFace datasets"""
    
    def __init__(self):
        self.datasets_dir = Path("datasets/chat")
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        
        # Curated list of high-quality datasets
        self.chat_datasets = [
            # Instruction datasets
            "databricks/databricks-dolly-15k",
            "tatsu-lab/alpaca",
            "GAIR/lima",
            "OpenAssistant/oasst1",
            "HuggingFaceH4/ultrachat_200k",
            "HuggingFaceH4/no_robots",
            "teknium/OpenHermes-2.5",
            "Intel/orca_dpo_pairs",
            "HuggingFaceH4/ultrafeedback_binarized",
            
            # Coding datasets
            "bigcode/starcoderdata",
            "codeparrot/github-code",
            "m-a-p/CodeFeedback-Filtered-Instruction",
            
            # Math/reasoning
            "meta-math/MetaMathQA",
            "microsoft/orca-math-word-problems-200k",
            
            # General knowledge
            "wikipedia",
            "wikimedia/wikipedia",
            
            # Conversation
            "lmsys/lmsys-chat-1m",
            "HuggingFaceH4/ShareGPT_V4.3",
            
            # Domain-specific
            "medalpaca/medical_meadow_mediqa",
            "MedRAG/textbooks",
        ]
        
        self.stats = {
            "started_at": datetime.now().isoformat(),
            "attempted": 0,
            "succeeded": 0,
            "failed": 0,
            "datasets": []
        }
    
    async def download_dataset(self, dataset_name: str, max_samples: int = 10000):
        """Download a single dataset from HuggingFace"""
        try:
            from datasets import load_dataset
            
            logger.info(f"📥 Downloading: {dataset_name}")
            self.stats["attempted"] += 1
            
            # Try to load dataset
            try:
                # Try with split
                ds = load_dataset(dataset_name, split=f"train[:{max_samples}]")
            except:
                try:
                    # Try without split specification
                    ds = load_dataset(dataset_name)
                    if isinstance(ds, dict) and "train" in ds:
                        ds = ds["train"].select(range(min(max_samples, len(ds["train"]))))
                    else:
                        ds = ds.select(range(min(max_samples, len(ds))))
                except Exception as e:
                    logger.warning(f"  ⚠️  Could not load {dataset_name}: {e}")
                    return False
            
            # Create output directory
            safe_name = dataset_name.replace("/", "_")
            output_dir = self.datasets_dir / safe_name
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "train.jsonl"
            
            # Convert to chat format
            converted = 0
            with open(output_file, 'w') as f:
                for item in ds:
                    try:
                        # Try different format patterns
                        messages = None
                        
                        if 'messages' in item:
                            messages = item['messages']
                        elif 'conversations' in item:
                            messages = item['conversations']
                        elif 'instruction' in item and 'response' in item:
                            messages = [
                                {"role": "user", "content": str(item['instruction'])},
                                {"role": "assistant", "content": str(item['response'])}
                            ]
                        elif 'prompt' in item and 'completion' in item:
                            messages = [
                                {"role": "user", "content": str(item['prompt'])},
                                {"role": "assistant", "content": str(item['completion'])}
                            ]
                        elif 'text' in item:
                            # For text-only datasets, create instruction
                            messages = [
                                {"role": "user", "content": "Explain this content"},
                                {"role": "assistant", "content": str(item['text'][:2000])}
                            ]
                        
                        if messages:
                            f.write(json.dumps({"messages": messages}) + '\n')
                            converted += 1
                            
                    except Exception as e:
                        continue
            
            if converted > 0:
                self.stats["succeeded"] += 1
                self.stats["datasets"].append({
                    "name": dataset_name,
                    "samples": converted,
                    "path": str(output_dir)
                })
                logger.info(f"  ✅ Success: {converted} samples")
                return True
            else:
                logger.warning(f"  ⚠️  No samples converted for {dataset_name}")
                self.stats["failed"] += 1
                return False
                
        except ImportError:
            logger.error("❌ HuggingFace datasets not installed: pip install datasets")
            return False
        except Exception as e:
            logger.error(f"  ❌ Error downloading {dataset_name}: {e}")
            self.stats["failed"] += 1
            return False
    
    async def collect_all(self, max_samples_per_dataset: int = 10000):
        """Collect all datasets"""
        logger.info("="*80)
        logger.info("🤗 HUGGINGFACE BULK COLLECTION")
        logger.info("="*80)
        logger.info(f"Datasets to collect: {len(self.chat_datasets)}")
        logger.info(f"Max samples per dataset: {max_samples_per_dataset}")
        logger.info("="*80)
        
        for dataset_name in self.chat_datasets:
            await self.download_dataset(dataset_name, max_samples_per_dataset)
        
        # Save report
        self.stats["completed_at"] = datetime.now().isoformat()
        report_dir = Path("data_out/data_collection")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / "huggingface_bulk_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        logger.info("\n" + "="*80)
        logger.info("✅ HUGGINGFACE COLLECTION COMPLETE!")
        logger.info(f"   Attempted: {self.stats['attempted']}")
        logger.info(f"   Succeeded: {self.stats['succeeded']}")
        logger.info(f"   Failed: {self.stats['failed']}")
        logger.info(f"   Success Rate: {self.stats['succeeded']/max(1, self.stats['attempted'])*100:.1f}%")
        logger.info(f"   Report: {report_file}")
        logger.info("="*80)


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HuggingFace Bulk Dataset Collector")
    parser.add_argument("--max-samples", type=int, default=10000,
                       help="Maximum samples per dataset")
    parser.add_argument("--quick", action="store_true",
                       help="Quick mode (1000 samples per dataset)")
    
    args = parser.parse_args()
    
    max_samples = 1000 if args.quick else args.max_samples
    
    collector = HuggingFaceBulkCollector()
    await collector.collect_all(max_samples_per_dataset=max_samples)


if __name__ == "__main__":
    asyncio.run(main())
