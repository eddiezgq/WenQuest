"""Model gateway: one place that talks to language models.

Providers: Claude (Anthropic API), DeepSeek (OpenAI-compatible API, registered for use in
mainland China) and a deterministic `fake` provider used by tests and offline demos.
Every call asks for JSON that matches a schema, so callers get structured data back.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx

from .moodle import EngineError


class AIError(EngineError):
    pass


def unpack(v: Any) -> Any:
    """Models sometimes return a nested list or object as a JSON string ("[{...}]"). Parse those back."""
    if isinstance(v, str):
        t = v.strip()
        if t[:1] in "[{" and t[-1:] in "]}":
            try:
                return unpack(json.loads(t))
            except ValueError:
                return v
        return v
    if isinstance(v, dict):
        return {k: unpack(x) for k, x in v.items()}
    if isinstance(v, list):
        return [unpack(x) for x in v]
    return v


class ModelGateway:
    def __init__(self, provider: str, http: httpx.AsyncClient, *, anthropic_key: str = "",
                 claude_model: str = "claude-sonnet-5", deepseek_key: str = "",
                 deepseek_model: str = "deepseek-chat", timeout: float = 180.0, fake_delay: float = 0.0):
        self.http = http
        self.anthropic_key = anthropic_key
        self.claude_model = claude_model
        self.deepseek_key = deepseek_key
        self.deepseek_model = deepseek_model
        self.timeout = timeout
        self.fake_delay = fake_delay
        if provider == "auto":
            provider = "claude" if anthropic_key else "deepseek" if deepseek_key else "none"
        self.provider = provider

    @property
    def available(self) -> bool:
        return self.provider in ("claude", "deepseek", "fake")

    async def json(self, *, system: str, prompt: str, schema: dict, max_tokens: int = 8000,
                   fake: Any = None) -> dict:
        if self.provider == "claude":
            return unpack(await self._claude(system, prompt, schema, max_tokens))
        if self.provider == "deepseek":
            return unpack(await self._deepseek(system, prompt, schema, max_tokens))
        if self.provider == "fake":
            if self.fake_delay:
                await asyncio.sleep(self.fake_delay)
            return fake() if callable(fake) else (fake or {})
        raise AIError("ai_unavailable", "no AI model is configured", 503)

    async def _claude(self, system: str, prompt: str, schema: dict, max_tokens: int) -> dict:
        body = {
            "model": self.claude_model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
            "tools": [{"name": "output", "description": "Return the result.", "input_schema": schema}],
            "tool_choice": {"type": "tool", "name": "output"},
        }
        headers = {"x-api-key": self.anthropic_key, "anthropic-version": "2023-06-01",
                   "content-type": "application/json"}
        data = await self._post("https://api.anthropic.com/v1/messages", body, headers)
        for block in data.get("content", []):
            if block.get("type") == "tool_use":
                return block.get("input") or {}
        raise AIError("ai_bad_output", "model returned no structured output", 502)

    async def _deepseek(self, system: str, prompt: str, schema: dict, max_tokens: int) -> dict:
        body = {
            "model": self.deepseek_model,
            "max_tokens": min(max_tokens, 8192),
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system + "\n\nReply with one JSON object that matches this JSON "
                                                       "Schema, and nothing else:\n" + json.dumps(schema)},
                {"role": "user", "content": prompt},
            ],
        }
        headers = {"Authorization": f"Bearer {self.deepseek_key}", "content-type": "application/json"}
        data = await self._post("https://api.deepseek.com/chat/completions", body, headers)
        try:
            return json.loads(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, ValueError) as exc:
            raise AIError("ai_bad_output", "model returned invalid JSON", 502) from exc

    async def _post(self, url: str, body: dict, headers: dict) -> dict:
        try:
            r = await self.http.post(url, json=body, headers=headers, timeout=self.timeout)
        except httpx.TimeoutException as exc:
            raise AIError("ai_timeout", "the model took too long", 504) from exc
        except httpx.HTTPError as exc:
            raise AIError("ai_unreachable", str(exc), 503) from exc
        if r.status_code == 429:
            raise AIError("ai_busy", "rate limited", 429)
        if r.status_code in (401, 403):
            raise AIError("ai_key_invalid", "the API key was rejected", 503)
        if r.status_code >= 400:
            raise AIError("ai_error", f"model API error {r.status_code}: {r.text[:300]}", 502)
        return r.json()
