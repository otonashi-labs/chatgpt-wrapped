#!/usr/bin/env python3
"""
ChatGPT Conversation Metadater v2

Enriches unrolled conversations with LLM-extracted metadata.
Uses Gemini 3 Flash Preview via OpenRouter with 0-100 scoring scales.

Usage:
    python metadate.py                           # Process all from default dirs
    python metadate.py --input ../unrolled/conversations --output ../wmeta_2/conversations
    python metadate.py --limit 5                 # Process only first 5
    python metadate.py --month 12-2025           # Process specific month
    python metadate.py --file path/to/conv.json  # Process single file
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

from config import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR
from llm_client import LLMClient
from extractor import extract_metadata, enrich_conversation


def parse_args():
    parser = argparse.ArgumentParser(
        description="Enrich ChatGPT conversations with LLM-extracted metadata"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Input directory with unrolled conversations"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for enriched conversations"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Process a single file instead of directory"
    )
    parser.add_argument(
        "--month",
        type=str,
        help="Process only specific month folder (e.g., 12-2025)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of conversations to process"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=True,
        help="Skip files that already exist in output (default: True)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without making API calls"
    )
    return parser.parse_args()


def find_conversations(
    input_dir: Path,
    month: str | None = None,
) -> list[Path]:
    """Find all conversation JSON files to process."""
    conversations = []
    
    if month:
        month_dir = input_dir / month
        if month_dir.exists():
            conversations = list(month_dir.glob("*.json"))
    else:
        conversations = list(input_dir.glob("**/*.json"))
    
    return sorted(conversations)


def get_output_path(input_path: Path, input_dir: Path, output_dir: Path) -> Path:
    """Calculate output path preserving folder structure."""
    relative = input_path.relative_to(input_dir)
    return output_dir / relative


def process_file(
    input_path: Path,
    output_path: Path,
    client: LLMClient,
    dry_run: bool = False,
) -> dict:
    """
    Process a single conversation file.
    
    Returns:
        Dict with status and details
    """
    # Read input
    with open(input_path, "r", encoding="utf-8") as f:
        conv = json.load(f)
    
    if dry_run:
        return {
            "status": "dry_run",
            "input": str(input_path),
            "output": str(output_path),
            "title": conv.get("title", "Untitled"),
        }
    
    # Extract metadata
    result = extract_metadata(conv, client)
    
    if not result["success"]:
        return {
            "status": "error",
            "input": str(input_path),
            "error": result["error"],
            "usage": result.get("usage", {}),
        }
    
    # Enrich and save
    enriched = enrich_conversation(conv, result["metadata"])
    
    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    
    return {
        "status": "success",
        "input": str(input_path),
        "output": str(output_path),
        "title": conv.get("title", "Untitled"),
        "relevance": result["metadata"].get("inferred_future_relevance_score", 0),
        "usage": result["usage"],
    }


def main():
    args = parse_args()
    
    # Resolve paths relative to script location
    script_dir = Path(__file__).parent
    input_dir = args.input if args.input.is_absolute() else script_dir / args.input
    output_dir = args.output if args.output.is_absolute() else script_dir / args.output
    
    print(f"📂 Input: {input_dir}")
    print(f"📂 Output: {output_dir}")
    
    # Handle single file mode
    if args.file:
        file_path = args.file if args.file.is_absolute() else script_dir / args.file
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 1
        
        conversations = [file_path]
        # For single file, output to same structure
        input_dir = file_path.parent.parent  # Go up from month folder
    else:
        conversations = find_conversations(input_dir, args.month)
    
    if not conversations:
        print("❌ No conversations found")
        return 1
    
    # Apply limit
    if args.limit:
        conversations = conversations[:args.limit]
    
    print(f"📊 Found {len(conversations)} conversations to process")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No API calls will be made\n")
    
    # Initialize client
    client = LLMClient() if not args.dry_run else None
    
    # Track stats
    stats = {
        "processed": 0,
        "skipped": 0,
        "errors": 0,
        "total_tokens": 0,
    }
    
    # Process each file
    for i, conv_path in enumerate(conversations):
        output_path = get_output_path(conv_path, input_dir, output_dir)
        
        # Skip existing
        if not args.force and output_path.exists():
            stats["skipped"] += 1
            continue
        
        # Process
        print(f"  → [{i+1}/{len(conversations)}] Processing: {conv_path.name}...", end="\r")
        result = process_file(conv_path, output_path, client, args.dry_run)
        
        if result["status"] == "success":
            stats["processed"] += 1
            usage = result.get("usage", {})
            stats["total_tokens"] += usage.get("total_tokens", 0)
            
            relevance = result.get("relevance", 0)
            print(f"  ✓ [{i+1}/{len(conversations)}] {result['title'][:50]} [rel:{relevance}]" + " " * 20)
            
        elif result["status"] == "error":
            stats["errors"] += 1
            print(f"  ✗ [{i+1}/{len(conversations)}] {conv_path.name}: {result['error'][:50]}")
            
        elif result["status"] == "dry_run":
            print(f"  📋 [{i+1}/{len(conversations)}] {result['title'][:50]}")
    
    # Summary
    print(f"\n✅ Done!")
    print(f"   Processed: {stats['processed']}")
    print(f"   Skipped: {stats['skipped']}")
    print(f"   Errors: {stats['errors']}")
    print(f"   Total tokens: {stats['total_tokens']:,}")
    
    return 0


if __name__ == "__main__":
    exit(main())

