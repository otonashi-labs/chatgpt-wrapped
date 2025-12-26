#!/usr/bin/env python3
"""
ChatGPT Conversation Metadater v2 (Async version)

Enriches unrolled conversations with LLM-extracted metadata using Gemini 3 Flash.
Processes conversations in parallel (default: 10 at a time).
"""

import json
import argparse
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Any

from config import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR
from llm_client import LLMClient
from extractor import extract_metadata, enrich_conversation, extract_conversation_text


def parse_args():
    parser = argparse.ArgumentParser(
        description="Enrich ChatGPT conversations with LLM-extracted metadata (Async)"
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
        "--concurrency",
        type=int,
        default=10,
        help="Number of concurrent requests (default: 10)"
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


def find_conversations(input_dir: Path, month: str | None = None) -> list[Path]:
    """Find all conversation JSON files to process."""
    if month:
        month_dir = input_dir / month
        if month_dir.exists():
            conversations = list(month_dir.glob("*.json"))
        else:
            conversations = []
    else:
        conversations = list(input_dir.glob("**/*.json"))
    return sorted(conversations)


def get_output_path(input_path: Path, input_dir: Path, output_dir: Path) -> Path:
    """Calculate output path preserving folder structure."""
    relative = input_path.relative_to(input_dir)
    return output_dir / relative


async def process_file_async(
    input_path: Path,
    output_path: Path,
    client: LLMClient,
    semaphore: asyncio.Semaphore,
    dry_run: bool = False,
    index: int = 0,
    total: int = 0,
) -> dict:
    """Process a single conversation file asynchronously."""
    async with semaphore:
        # Read input
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                conv = json.load(f)
        except Exception as e:
            return {"status": "error", "input": str(input_path), "error": f"Read error: {e}"}

        if dry_run:
            return {
                "status": "dry_run",
                "input": str(input_path),
                "title": conv.get("title", "Untitled"),
            }

        print(f"  → [{index}/{total}] Processing: {input_path.name}...", end="\r")

        # Use extractor logic but async
        from extractor import load_system_prompt, build_user_prompt
        
        conv_text = extract_conversation_text(conv)
        MAX_CHARS = 500_000
        if len(conv_text) > MAX_CHARS:
            conv_text = conv_text[:MAX_CHARS] + "\n\n[CONVERSATION TRUNCATED]"
            
        system_prompt = load_system_prompt()
        user_prompt = build_user_prompt(conv_text)
        
        result = await client.complete_async(system_prompt, user_prompt)

        if not result["success"]:
            print(f"  ✗ [{index}/{total}] Error processing {input_path.name}: {result['error'][:50]}")
            return {
                "status": "error",
                "input": str(input_path),
                "error": result["error"],
                "usage": result.get("usage", {}),
            }

        # Enrich and save
        enriched = enrich_conversation(conv, result["data"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(enriched, f, indent=2, ensure_ascii=False)

        relevance = result["data"].get("inferred_future_relevance_score", 0)
        print(f"  ✓ [{index}/{total}] {conv.get('title', 'Untitled')[:50]} [rel:{relevance}]" + " " * 20)
        
        return {
            "status": "success",
            "input": str(input_path),
            "output": str(output_path),
            "title": conv.get("title", "Untitled"),
            "relevance": relevance,
            "usage": result["usage"],
        }


async def main_async():
    args = parse_args()
    
    script_dir = Path(__file__).parent
    input_dir = args.input if args.input.is_absolute() else script_dir / args.input
    output_dir = args.output if args.output.is_absolute() else script_dir / args.output
    
    print(f"📂 Input: {input_dir}")
    print(f"📂 Output: {output_dir}")
    
    if args.file:
        conversations = [args.file if args.file.is_absolute() else script_dir / args.file]
        input_dir = conversations[0].parent.parent
    else:
        conversations = find_conversations(input_dir, args.month)
    
    if not conversations:
        print("❌ No conversations found")
        return 1
        
    if args.limit:
        conversations = conversations[:args.limit]
        
    print(f"📊 Found {len(conversations)} conversations to process (Concurrency: {args.concurrency})")
    
    client = LLMClient() if not args.dry_run else None
    semaphore = asyncio.Semaphore(args.concurrency)
    
    tasks = []
    stats = {"processed": 0, "skipped": 0, "errors": 0, "total_tokens": 0}
    
    for i, conv_path in enumerate(conversations, 1):
        output_path = get_output_path(conv_path, input_dir, output_dir)
        if not args.force and output_path.exists():
            stats["skipped"] += 1
            continue
            
        tasks.append(process_file_async(conv_path, output_path, client, semaphore, args.dry_run, i, len(conversations)))
        
    if not tasks:
        print("\n✅ All files already processed (use --force to re-process)")
        return 0

    results = await asyncio.gather(*tasks)
    
    for result in results:
        if result["status"] == "success":
            stats["processed"] += 1
            stats["total_tokens"] += result.get("usage", {}).get("total_tokens", 0)
        elif result["status"] == "error":
            stats["errors"] += 1
            
    print(f"\n✅ Done!")
    print(f"   Processed: {stats['processed']}")
    print(f"   Skipped: {stats['skipped']}")
    print(f"   Errors: {stats['errors']}")
    print(f"   Total tokens: {stats['total_tokens']:,}")
    
    return 0


if __name__ == "__main__":
    asyncio.run(main_async())
