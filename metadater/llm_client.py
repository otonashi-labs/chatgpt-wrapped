"""
LLM client for OpenRouter API with retry logic and async support.
"""

import json
import time
import httpx
import asyncio
from typing import Any

from config import (
    OPENROUTER_API_KEY, 
    OPENROUTER_BASE_URL, 
    MODEL, 
    DELAY_BETWEEN_REQUESTS,
    MAX_RETRIES,
    RETRY_BACKOFF,
)


class LLMClient:
    """Simple client for OpenRouter API with retry logic."""
    
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.model = model or MODEL
        self.base_url = base_url or OPENROUTER_BASE_URL
        self.last_request_time = 0
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")
    
    def _rate_limit(self):
        """Minimal delay between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < DELAY_BETWEEN_REQUESTS:
            time.sleep(DELAY_BETWEEN_REQUESTS - elapsed)
        self.last_request_time = time.time()

    async def _async_rate_limit(self):
        """Minimal delay between requests (async)."""
        elapsed = time.time() - self.last_request_time
        if elapsed < DELAY_BETWEEN_REQUESTS:
            await asyncio.sleep(DELAY_BETWEEN_REQUESTS - elapsed)
        self.last_request_time = time.time()

    def _parse_response(self, raw_content: str, usage: dict) -> dict:
        """Helper to parse LLM response JSON."""
        try:
            content = raw_content.strip()
            if content.startswith("```"):
                # Remove markdown code blocks
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()
            
            data = json.loads(content)
            return {
                "success": True,
                "data": data,
                "raw": raw_content,
                "usage": usage,
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON parse error: {e}",
                "raw": raw_content,
                "usage": usage,
            }

    async def complete_async(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        """Async completion request with retry logic."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/metadater",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            await self._async_rate_limit()
            
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    
                    if response.status_code == 429:
                        if attempt < MAX_RETRIES:
                            wait_time = RETRY_BACKOFF ** (attempt + 1)
                            await asyncio.sleep(wait_time)
                            continue
                        return {"success": False, "error": "Rate limited", "usage": {}}
                    
                    response.raise_for_status()
                    
                result = response.json()
                raw_content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                return self._parse_response(raw_content, usage)
                    
            except Exception as e:
                last_error = str(e)
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_BACKOFF ** (attempt + 1))
                    continue
        
        return {"success": False, "error": last_error, "usage": {}}

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        """Synchronous completion request."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/metadater",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            self._rate_limit()
            try:
                with httpx.Client(timeout=120.0) as client:
                    response = client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    if response.status_code == 429 and attempt < MAX_RETRIES:
                        time.sleep(RETRY_BACKOFF ** (attempt + 1))
                        continue
                    response.raise_for_status()
                    
                result = response.json()
                raw_content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                return self._parse_response(raw_content, usage)
            except Exception as e:
                last_error = str(e)
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF ** (attempt + 1))
                    continue
        return {"success": False, "error": last_error, "usage": {}}
