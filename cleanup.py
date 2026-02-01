#!/usr/bin/env python3
"""
Data cleanup utility for Podcast AI project
Removes temporary files and processed data after specified time period
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Default cleanup policy: remove files older than 7 days
DEFAULT_AGE_DAYS = 7

def cleanup_old_files(directory: Path, age_days: int = DEFAULT_AGE_DAYS):
    """Remove files older than specified days"""
    if not directory.exists():
        return 0
    
    cutoff_time = time.time() - (age_days * 24 * 60 * 60)
    removed_count = 0
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    print(f"Removed: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")
    
    return removed_count

def cleanup_processed_data(age_days: int = DEFAULT_AGE_DAYS):
    """Clean up processed audio files and outputs"""
    print(f"Starting cleanup (files older than {age_days} days)...")
    
    # Clean data directory (uploaded audio files)
    data_removed = cleanup_old_files(DATA_DIR, age_days)
    
    # Clean outputs directory (processed JSON files)
    outputs_removed = cleanup_old_files(OUTPUTS_DIR, age_days)
    
    total_removed = data_removed + outputs_removed
    
    print(f"\nCleanup Summary:")
    print(f"  Data files removed: {data_removed}")
    print(f"  Output files removed: {outputs_removed}")
    print(f"  Total files removed: {total_removed}")
    
    return total_removed

def list_old_files(directory: Path, age_days: int = DEFAULT_AGE_DAYS):
    """List files that would be removed (dry run)"""
    if not directory.exists():
        return []
    
    cutoff_time = time.time() - (age_days * 24 * 60 * 60)
    old_files = []
    
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
            old_files.append(file_path)
    
    return old_files

def dry_run(age_days: int = DEFAULT_AGE_DAYS):
    """Show what files would be removed without actually removing them"""
    print(f"Dry run - files older than {age_days} days would be removed:")
    
    # Check data directory
    old_data_files = list_old_files(DATA_DIR, age_days)
    print(f"\nData directory ({DATA_DIR}):")
    if old_data_files:
        for file_path in old_data_files:
            age = (time.time() - file_path.stat().st_mtime) / (24 * 60 * 60)
            print(f"  {file_path.name} (age: {age:.1f} days)")
    else:
        print("  No old files found")
    
    # Check outputs directory
    old_output_files = list_old_files(OUTPUTS_DIR, age_days)
    print(f"\nOutputs directory ({OUTPUTS_DIR}):")
    if old_output_files:
        for file_path in old_output_files:
            age = (time.time() - file_path.stat().st_mtime) / (24 * 60 * 60)
            print(f"  {file_path.name} (age: {age:.1f} days)")
    else:
        print("  No old files found")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up old Podcast AI data files")
    parser.add_argument("--days", type=int, default=DEFAULT_AGE_DAYS,
                       help=f"Age threshold in days (default: {DEFAULT_AGE_DAYS})")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be removed without actually removing")
    
    args = parser.parse_args()
    
    if args.dry_run:
        dry_run(args.days)
    else:
        cleanup_processed_data(args.days)