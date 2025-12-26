"""
LLM client for OpenRouter API with retry logic.
"""

import json
import time
import httpx
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
    
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        """
        Send a completion request and return parsed JSON response.
        Includes retry logic with exponential backoff for rate limits.
        
        Returns dict with:
          - success: bool
          - data: parsed JSON (if success)
          - error: error message (if failed)
          - raw: raw response text
          - usage: token usage stats
        """
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
                with httpx.Client(timeout=300.0) as client:  # 5 min for large conversations
                    response = client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    
                    # Handle rate limiting with retry
                    if response.status_code == 429:
                        if attempt < MAX_RETRIES:
                            wait_time = RETRY_BACKOFF ** (attempt + 1)
                            time.sleep(wait_time)
                            continue
                        else:
                            return {
                                "success": False,
                                "error": f"Rate limited after {MAX_RETRIES} retries",
                                "raw": None,
                                "usage": {},
                            }
                    
                    response.raise_for_status()
                    
                result = response.json()
                raw_content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                
                # Parse JSON from response
                try:
                    # Try to extract JSON if wrapped in markdown
                    content = raw_content.strip()
                    if content.startswith("```"):
                        # Remove markdown code blocks
                        lines = content.split("\n")
                        content = "\n".join(lines[1:-1])
                    
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
                    
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP error: {e.response.status_code} - {e.response.text}"
                if attempt < MAX_RETRIES and e.response.status_code in (429, 500, 502, 503, 504):
                    wait_time = RETRY_BACKOFF ** (attempt + 1)
                    time.sleep(wait_time)
                    continue
                    
            except Exception as e:
                last_error = f"Request error: {str(e)}"
                if attempt < MAX_RETRIES:
                    wait_time = RETRY_BACKOFF ** (attempt + 1)
                    time.sleep(wait_time)
                    continue
        
        return {
            "success": False,
            "error": last_error or "Unknown error after retries",
            "raw": None,
            "usage": {},
        }
