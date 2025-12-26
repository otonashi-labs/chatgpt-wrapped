#!/usr/bin/env python3
"""
ChatGPT Wrapped - Clean Test Runner (Async)
1. Samples N conversations from raw data
2. Cleans all output directories
3. Runs the full pipeline
"""

import os
import subprocess
import sys
import json
import random
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Configuration
TARGET_COUNT = 100
ROOT_DIR = Path("/Users/goak/Thinking/simak/chatgpt_wrapped")
DATA_DIR = ROOT_DIR / "data"
RAW_CONV = DATA_DIR / "conversations" / "conversations_raw.json"
TEST_CONV = DATA_DIR / "conversations" / "conversations.json"

def run_cmd(cmd, cwd=None):
    print(f"🚀 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Command failed with return code {result.returncode}")
        sys.exit(1)

def clean_dir(path):
    print(f"🧹 Cleaning {path}...")
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return
    
    for item in path.iterdir():
        if item.name == ".gitkeep":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

def sample_data(count):
    print(f"📝 Sampling {count} conversations from raw data...")
    if not RAW_CONV.exists():
        print(f"❌ Raw data not found at {RAW_CONV}")
        sys.exit(1)
        
    with open(RAW_CONV, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Group by month
    by_month = defaultdict(list)
    for conv in data:
        create_time = conv.get('create_time')
        if create_time:
            dt = datetime.fromtimestamp(create_time)
            month_key = dt.strftime("%Y-%m")
            by_month[month_key].append(conv)
    
    sampled = []
    # Simple fair sampling
    pool = {m: list(c) for m, c in by_month.items()}
    needed = count
    while needed > 0 and pool:
        current_months = list(pool.keys())
        for m in current_months:
            if needed <= 0: break
            if not pool[m]:
                del pool[m]
                continue
            conv = random.choice(pool[m])
            sampled.append(conv)
            pool[m].remove(conv)
            needed -= 1
            
    with open(TEST_CONV, 'w', encoding='utf-8') as f:
        json.dump(sampled, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(sampled)} sampled conversations to {TEST_CONV}")

def main():
    # 1. Sample fresh data
    sample_data(TARGET_COUNT)
    
    # 2. Clean output directories to avoid doubling/duplicates
    clean_dir(DATA_DIR / "unrolled")
    clean_dir(DATA_DIR / "wmeta")
    clean_dir(DATA_DIR / "stats")
    
    # 3. Run Pipeline Steps
    print("\n--- STEP 1: Unrolling ---")
    run_cmd([sys.executable, "unroller/unroll.py", str(TEST_CONV)], cwd=ROOT_DIR)
    
    print("\n--- STEP 2: AI Metadata Enrichment (ASYNC) ---")
    run_cmd([sys.executable, "metadater/metadate.py", "--concurrency", "10"], cwd=ROOT_DIR)
    
    print("\n--- STEP 3: Aggregation ---")
    run_cmd([sys.executable, "wrapped/aggregate.py"], cwd=ROOT_DIR)
    
    print("\n--- STEP 4: Generate HTML ---")
    try:
        run_cmd(["bun", "run", "generate"], cwd=ROOT_DIR / "wrapped")
        print(f"\n✨ Test Complete! Open {ROOT_DIR}/wrapped/wrapped.html")
    except Exception:
        print("\n⚠️ Bun not found, skipping HTML generation.")

if __name__ == "__main__":
    main()
