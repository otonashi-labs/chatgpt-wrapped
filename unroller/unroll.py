#!/usr/bin/env python3
"""
ChatGPT Conversations Unroller

Unpacks a single conversations.json export into individual JSON files,
organized by month and enriched with useful metadata.

Usage:
    python unroll.py /path/to/conversations.json /path/to/output/
    python unroll.py /path/to/conversations.json  # outputs to ./conversations/
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Any
from collections import defaultdict

from enricher import enrich_conversation


def parse_args():
    parser = argparse.ArgumentParser(
        description="Unpack ChatGPT conversations.json into organized individual files"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to conversations.json"
    )
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=Path(__file__).parent.parent / "data" / "unrolled",
        help="Output directory (default: ../data/unrolled)"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print JSON output (default: True)"
    )
    parser.add_argument(
        "--no-pretty",
        action="store_false",
        dest="pretty",
        help="Minify JSON output"
    )
    return parser.parse_args()


def get_month_folder(timestamp: float) -> str:
    """Convert Unix timestamp to MM-YYYY folder name."""
    dt = datetime.fromtimestamp(timestamp)
    return f"{dt.month:02d}-{dt.year}"


def get_filename(conv_id: str) -> str:
    """Get filename from conversation ID."""
    return conv_id if conv_id else "unknown"


def unroll_conversations(input_path: Path, output_path: Path, pretty: bool = True):
    """Main unrolling logic."""
    
    print(f"📂 Reading {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        conversations = json.load(f)
    
    print(f"📊 Found {len(conversations)} conversations")
    
    # Track stats
    stats = defaultdict(int)
    months_created = set()
    
    for i, conv in enumerate(conversations):
        # Get creation time for folder organization
        create_time = conv.get("create_time")
        if not create_time:
            print(f"  ⚠️  Skipping conversation without create_time: {conv.get('id', 'unknown')}")
            stats["skipped"] += 1
            continue
        
        # Determine output folder
        month_folder = get_month_folder(create_time)
        folder_path = output_path / month_folder
        
        # Create folder if needed
        if month_folder not in months_created:
            folder_path.mkdir(parents=True, exist_ok=True)
            months_created.add(month_folder)
        
        # Enrich conversation with metadata
        enriched = enrich_conversation(conv)
        
        # Generate filename
        filename = get_filename(conv.get("id") or conv.get("conversation_id", "unknown"))
        file_path = folder_path / f"{filename}.json"
        
        # Handle duplicates
        counter = 1
        while file_path.exists():
            file_path = folder_path / f"{filename}_{counter}.json"
            counter += 1
        
        # Write file
        with open(file_path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(enriched, f, indent=2, ensure_ascii=False)
            else:
                json.dump(enriched, f, ensure_ascii=False)
        
        stats["processed"] += 1
        stats[month_folder] += 1
        
        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"  ✓ Processed {i + 1}/{len(conversations)}")
    
    # Print summary
    print(f"\n✅ Done!")
    print(f"   Processed: {stats['processed']}")
    print(f"   Skipped: {stats['skipped']}")
    print(f"\n📁 Folders created:")
    for month in sorted(months_created):
        print(f"   {month}: {stats[month]} conversations")


def main():
    args = parse_args()
    
    if not args.input.exists():
        print(f"❌ Input file not found: {args.input}")
        return 1
    
    unroll_conversations(args.input, args.output, args.pretty)
    return 0


if __name__ == "__main__":
    exit(main())

