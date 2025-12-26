#!/usr/bin/env python3
"""
ChatGPT Wrapped 2025 - Main Runner
Orchestrates the full pipeline: unroll -> metadate -> aggregate -> generate
"""

import os
import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, cwd=None):
    print(f"🚀 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Command failed with return code {result.returncode}")
        sys.exit(1)

def main():
    root_dir = Path(__file__).parent
    data_dir = root_dir / "data"
    conv_json = data_dir / "conversations" / "conversations.json"

    # 1. Check if conversations.json exists
    if not conv_json.exists():
        print(f"❌ Error: {conv_json} not found.")
        print("Please place your exported conversations.json in data/conversations/")
        sys.exit(1)

    # 2. Unroll
    print("\n--- STEP 1: Unrolling conversations ---")
    run_cmd([sys.executable, "unroller/unroll.py", str(conv_json)], cwd=root_dir)

    # 3. Metadate
    print("\n--- STEP 2: Enriching with metadata (AI processing) ---")
    print("This step requires OPENROUTER_API_KEY in your .env file.")
    run_cmd([sys.executable, "metadater/metadate.py"], cwd=root_dir)

    # 4. Aggregate
    print("\n--- STEP 3: Aggregating statistics ---")
    run_cmd([sys.executable, "wrapped/aggregate.py"], cwd=root_dir)

    # 5. Generate HTML
    print("\n--- STEP 4: Generating Wrapped HTML ---")
    # Check if bun is installed
    try:
        subprocess.run(["bun", "--version"], capture_output=True, check=True)
        run_cmd(["bun", "run", "generate"], cwd=root_dir / "wrapped")
        print("\n✨ Done! Open chatgpt_wrapped/wrapped/wrapped.html in your browser.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n⚠️  'bun' not found. Please install bun (https://bun.sh) to generate the HTML,")
        print("or run 'npm install && npm run generate' in the 'wrapped' directory.")

if __name__ == "__main__":
    main()

