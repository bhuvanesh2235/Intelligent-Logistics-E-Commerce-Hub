"""
resplit.py -- Re-run class discovery and split without re-downloading
Run this after fixing the discover_classes mapping.
"""
import os, sys
from dotenv import load_dotenv
load_dotenv()

from utils import banner
from preprocessing import discover_classes, create_splits, plot_class_distribution, plot_sample_grid, generate_report

RAW_DIR = os.getenv("DATA_RAW_DIR", "data/raw")

banner("RESPLITTING WITH FIXED CLASS MAPPING")
class_map = discover_classes(RAW_DIR)
print(f"Classes found: {list(class_map.keys())}")
print(f"Total images : {sum(len(v) for v in class_map.values())}")

stats = create_splits(class_map)
plot_class_distribution(stats)
plot_sample_grid(class_map)
generate_report(stats, class_map)

banner("RESPLIT COMPLETE")
print(f"  Classes     : {list(class_map.keys())}")
print(f"  Train images: {stats['total']['train']}")
print(f"  Val images  : {stats['total']['val']}")
print(f"  Test images : {stats['total']['test']}")
print(f"  Skipped     : {stats['total']['skipped']}")
