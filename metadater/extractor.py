"""
Conversation metadata extractor.

Extracts full conversation content including metadata for LLM analysis.
Gemini 3 Flash has 1M token context - we can send much more data.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from llm_client import LLMClient
from prompts import load_system_prompt, build_user_prompt


def format_timestamp(ts: float | None) -> str:
    """Convert Unix timestamp to readable format."""
    if not ts:
        return "unknown"
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "unknown"


def extract_message_metadata(msg: dict) -> dict:
    """Extract useful metadata from a message object."""
    metadata = msg.get("metadata", {})
    author = msg.get("author", {})
    
    result = {
        "role": author.get("role", "unknown"),
        "model": metadata.get("model_slug") or metadata.get("default_model_slug"),
        "created": format_timestamp(msg.get("create_time")),
    }
    
    # Add interesting metadata flags
    if metadata.get("is_complete") is False:
        result["incomplete"] = True
    if metadata.get("finish_details", {}).get("type"):
        result["finish_type"] = metadata["finish_details"]["type"]
    if metadata.get("voice_mode_message"):
        result["voice_mode"] = True
    if author.get("name"):  # Plugin/tool name
        result["tool"] = author["name"]
    if metadata.get("invoked_plugin"):
        result["plugin"] = metadata["invoked_plugin"].get("namespace")
    if metadata.get("gizmo_id"):
        result["gpt_id"] = metadata["gizmo_id"]
    if metadata.get("attachments"):
        result["attachments"] = len(metadata["attachments"])
    
    # Filter out None values
    return {k: v for k, v in result.items() if v is not None}


def extract_content_text(content: dict) -> str:
    """Extract text content from a message content object."""
    parts = content.get("parts", [])
    text_parts = []
    
    for part in parts:
        if isinstance(part, str):
            text_parts.append(part)
        elif isinstance(part, dict):
            ct = part.get("content_type")
            if ct == "audio_transcription":
                text_parts.append(f"[AUDIO TRANSCRIPTION]\n{part.get('text', '')}")
            elif ct == "image_asset_pointer":
                text_parts.append("[IMAGE]")
            elif ct == "code":
                lang = part.get("language", "")
                code = part.get("text", "")
                text_parts.append(f"```{lang}\n{code}\n```")
            elif ct == "execution_output":
                text_parts.append(f"[EXECUTION OUTPUT]\n{part.get('text', '')}")
            elif ct == "tether_browsing_display":
                text_parts.append(f"[WEB BROWSING]\n{part.get('result', '')}")
            elif ct == "tether_quote":
                text_parts.append(f"[QUOTE: {part.get('title', '')}]\n{part.get('text', '')}")
            elif "text" in part:
                text_parts.append(part["text"])
    
    return "\n".join(text_parts).strip()


def extract_conversation_text(conv: dict) -> str:
    """
    Extract full conversation content with metadata for LLM analysis.
    
    Now includes:
    - Full message text (no truncation)
    - Message metadata (model, timestamps, tools)
    - Conversation-level metadata
    """
    lines = []
    
    # === CONVERSATION HEADER ===
    lines.append("=" * 60)
    lines.append("CONVERSATION METADATA")
    lines.append("=" * 60)
    
    title = conv.get("title", "Untitled")
    lines.append(f"Title: {title}")
    
    # Timestamps
    timestamps = conv.get("timestamps", {})
    if timestamps:
        lines.append(f"Created: {timestamps.get('created_at', 'unknown')}")
        lines.append(f"Updated: {timestamps.get('updated_at', 'unknown')}")
    
    # Conversation-level metadata
    if conv.get("default_model_slug"):
        lines.append(f"Default Model: {conv['default_model_slug']}")
    if conv.get("gizmo_id"):
        lines.append(f"Custom GPT ID: {conv['gizmo_id']}")
    if conv.get("conversation_template_id"):
        lines.append(f"Template: {conv['conversation_template_id']}")
    if conv.get("is_archived"):
        lines.append("Status: ARCHIVED")
    
    # Voice mode info
    if conv.get("voice"):
        lines.append(f"Voice Mode: {conv['voice']}")
    
    # Async status
    async_status = conv.get("async_status")
    if async_status:
        lines.append(f"Async Status: {async_status}")
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("MESSAGES")
    lines.append("=" * 60)
    lines.append("")
    
    # === EXTRACT AND SORT MESSAGES ===
    mapping = conv.get("mapping", {})
    messages = []
    
    for node_id, node in mapping.items():
        msg = node.get("message")
        if not msg:
            continue
        
        # Skip hidden system messages
        metadata = msg.get("metadata", {})
        if metadata.get("is_visually_hidden_from_conversation"):
            continue
        
        content = msg.get("content", {})
        text = extract_content_text(content)
        
        # Skip empty messages
        if not text:
            continue
        
        msg_meta = extract_message_metadata(msg)
        create_time = msg.get("create_time", 0)
        
        messages.append({
            "meta": msg_meta,
            "text": text,
            "time": create_time or 0,
        })
    
    # Sort by time
    messages.sort(key=lambda m: m["time"])
    
    # === FORMAT MESSAGES ===
    for i, msg in enumerate(messages, 1):
        meta = msg["meta"]
        role = meta.pop("role", "unknown").upper()
        
        # Build metadata line
        meta_parts = []
        if meta.get("model"):
            meta_parts.append(f"model={meta['model']}")
        if meta.get("tool"):
            meta_parts.append(f"tool={meta['tool']}")
        if meta.get("plugin"):
            meta_parts.append(f"plugin={meta['plugin']}")
        if meta.get("voice_mode"):
            meta_parts.append("voice")
        if meta.get("attachments"):
            meta_parts.append(f"attachments={meta['attachments']}")
        if meta.get("incomplete"):
            meta_parts.append("INCOMPLETE")
        
        # Message header
        header = f"[{role}]"
        if meta.get("created") and meta["created"] != "unknown":
            header += f" @ {meta['created']}"
        if meta_parts:
            header += f" ({', '.join(meta_parts)})"
        
        lines.append(header)
        lines.append(msg["text"])
        lines.append("")
    
    return "\n".join(lines)


def extract_metadata(
    conv: dict,
    client: LLMClient | None = None,
) -> dict[str, Any]:
    """
    Extract metadata from a conversation using LLM.
    
    Args:
        conv: Parsed conversation JSON
        client: LLM client instance (creates new one if not provided)
    
    Returns:
        Dict with:
          - success: bool
          - metadata: extracted metadata (if success)
          - error: error message (if failed)
          - usage: token usage stats
    """
    if client is None:
        client = LLMClient()
    
    # Extract full conversation text (no truncation)
    conv_text = extract_conversation_text(conv)
    
    # Only truncate for extremely long conversations (>500k chars ~ 125k tokens)
    # Gemini 3 Flash has 1M token input limit
    MAX_CHARS = 500_000
    if len(conv_text) > MAX_CHARS:
        conv_text = conv_text[:MAX_CHARS] + "\n\n[CONVERSATION TRUNCATED - exceeded 500k chars]"
    
    # Build prompts
    system_prompt = load_system_prompt()
    user_prompt = build_user_prompt(conv_text)
    
    # Call LLM
    result = client.complete(system_prompt, user_prompt)
    
    if result["success"]:
        return {
            "success": True,
            "metadata": result["data"],
            "usage": result["usage"],
        }
    else:
        return {
            "success": False,
            "error": result["error"],
            "raw": result.get("raw"),
            "usage": result.get("usage", {}),
        }


def enrich_conversation(
    conv: dict,
    metadata: dict,
) -> dict:
    """
    Merge extracted metadata into conversation JSON.
    Preserves original structure and adds 'llm_meta' section.
    """
    enriched = conv.copy()
    enriched["llm_meta"] = metadata
    return enriched
