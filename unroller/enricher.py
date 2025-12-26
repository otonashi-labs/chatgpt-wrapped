"""
Conversation Enricher

Extracts and computes useful metadata from ChatGPT conversations.
"""

from typing import Any
from datetime import datetime


def estimate_tokens(text: str) -> int:
    """
    Rough token estimation (approx 4 chars per token for English).
    For accurate counts, use tiktoken library.
    """
    if not text:
        return 0
    return len(text) // 4


def extract_text_from_parts(parts: list) -> str:
    """Extract all text content from message parts."""
    texts = []
    for part in parts:
        if isinstance(part, str):
            texts.append(part)
        elif isinstance(part, dict):
            # Handle special content types
            if part.get("content_type") == "audio_transcription":
                texts.append(part.get("text", ""))
    return "\n".join(texts)


def flatten_messages(mapping: dict) -> list[dict]:
    """
    Convert tree structure to flat list of messages, ordered by time.
    Returns list of message dicts with role, content, timestamp, etc.
    """
    messages = []
    
    for node_id, node in mapping.items():
        msg = node.get("message")
        if not msg:
            continue
        
        author = msg.get("author", {})
        role = author.get("role")
        
        # Skip hidden system messages
        metadata = msg.get("metadata", {})
        if metadata.get("is_visually_hidden_from_conversation"):
            continue
        
        content = msg.get("content", {})
        parts = content.get("parts", [])
        text = extract_text_from_parts(parts)
        
        # Skip empty messages
        if not text and content.get("content_type") == "text":
            continue
        
        messages.append({
            "id": msg.get("id"),
            "role": role,
            "text": text,
            "content_type": content.get("content_type"),
            "create_time": msg.get("create_time"),
            "model_slug": metadata.get("model_slug"),
            "has_image": any(
                isinstance(p, dict) and p.get("content_type") == "image_asset_pointer"
                for p in parts
            ),
            "has_audio": any(
                isinstance(p, dict) and p.get("content_type") == "audio_transcription"
                for p in parts
            ),
        })
    
    # Sort by create_time (None values go to beginning)
    messages.sort(key=lambda m: m.get("create_time") or 0)
    
    return messages


def compute_stats(messages: list[dict]) -> dict:
    """Compute statistics from flattened messages."""
    
    stats = {
        "total_messages": 0,
        "messages_by_role": {},
        "tokens_by_role": {},
        "total_tokens": 0,
        "user_tokens": 0,
        "assistant_tokens": 0,
        "models_used": set(),
        "has_images": False,
        "has_audio": False,
        "image_count": 0,
        "audio_count": 0,
        "first_message_time": None,
        "last_message_time": None,
        "duration_seconds": None,
        "word_count": 0,
    }
    
    for msg in messages:
        role = msg.get("role", "unknown")
        text = msg.get("text", "")
        tokens = estimate_tokens(text)
        
        # Count messages by role
        stats["messages_by_role"][role] = stats["messages_by_role"].get(role, 0) + 1
        stats["total_messages"] += 1
        
        # Count tokens by role
        stats["tokens_by_role"][role] = stats["tokens_by_role"].get(role, 0) + tokens
        stats["total_tokens"] += tokens
        
        if role == "user":
            stats["user_tokens"] += tokens
        elif role == "assistant":
            stats["assistant_tokens"] += tokens
        
        # Track models
        model = msg.get("model_slug")
        if model:
            stats["models_used"].add(model)
        
        # Track media
        if msg.get("has_image"):
            stats["has_images"] = True
            stats["image_count"] += 1
        if msg.get("has_audio"):
            stats["has_audio"] = True
            stats["audio_count"] += 1
        
        # Track timestamps
        create_time = msg.get("create_time")
        if create_time:
            if stats["first_message_time"] is None or create_time < stats["first_message_time"]:
                stats["first_message_time"] = create_time
            if stats["last_message_time"] is None or create_time > stats["last_message_time"]:
                stats["last_message_time"] = create_time
        
        # Word count
        if text:
            stats["word_count"] += len(text.split())
    
    # Calculate duration
    if stats["first_message_time"] and stats["last_message_time"]:
        stats["duration_seconds"] = stats["last_message_time"] - stats["first_message_time"]
    
    # Convert set to list for JSON serialization
    stats["models_used"] = sorted(list(stats["models_used"]))
    
    return stats


def format_duration(seconds: float | None) -> str | None:
    """Format duration in human-readable form."""
    if seconds is None:
        return None
    
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def enrich_conversation(conv: dict) -> dict:
    """
    Enrich a conversation with computed metadata.
    
    Returns a new dict with:
    - Original fields preserved
    - New 'meta' section with computed stats
    - Timestamps converted to ISO format for readability
    """
    
    # Flatten messages for analysis
    mapping = conv.get("mapping", {})
    messages = flatten_messages(mapping)
    
    # Compute stats
    stats = compute_stats(messages)
    
    # Build enriched metadata
    meta = {
        "total_messages": stats["total_messages"],
        "messages_by_role": stats["messages_by_role"],
        "total_tokens": stats["total_tokens"],
        "user_tokens": stats["user_tokens"],
        "assistant_tokens": stats["assistant_tokens"],
        "tokens_by_role": stats["tokens_by_role"],
        "models_used": stats["models_used"],
        "primary_model": conv.get("default_model_slug"),
        "duration_seconds": stats["duration_seconds"],
        "duration_human": format_duration(stats["duration_seconds"]),
        "word_count": stats["word_count"],
        "has_images": stats["has_images"],
        "has_audio": stats["has_audio"],
        "image_count": stats["image_count"],
        "audio_count": stats["audio_count"],
        "is_voice_conversation": conv.get("voice") is not None,
        "voice_name": conv.get("voice"),
    }
    
    # Format timestamps
    create_time = conv.get("create_time")
    update_time = conv.get("update_time")
    
    timestamps = {
        "created_at": datetime.fromtimestamp(create_time).isoformat() if create_time else None,
        "updated_at": datetime.fromtimestamp(update_time).isoformat() if update_time else None,
        "created_unix": create_time,
        "updated_unix": update_time,
    }
    
    # Build enriched conversation
    enriched = {
        # Core identifiers
        "id": conv.get("id") or conv.get("conversation_id"),
        "title": conv.get("title"),
        
        # Timestamps (human-readable at top)
        "timestamps": timestamps,
        
        # Computed metadata
        "meta": meta,
        
        # Original flags
        "is_archived": conv.get("is_archived", False),
        "is_starred": conv.get("is_starred"),
        
        # Full message tree (preserved for data integrity)
        "mapping": mapping,
        
        # Preserve any other original fields
        "safe_urls": conv.get("safe_urls"),
        "gizmo_id": conv.get("gizmo_id"),
    }
    
    return enriched

