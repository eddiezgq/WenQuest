"""Model gateway: one place that talks to language models.

Providers: Claude (Anthropic API), DeepSeek (OpenAI-compatible API, registered for use in
mainland China) and a deterministic `fake` provider used by tests and offline demos.
Every call asks for JSON that matches a schema, so callers get structured data back.
"""
from __future__ import annotations

import asyncio
import json
import re
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

    @property
    def sees_images(self) -> bool:
        return self.provider in ("claude", "fake")

    async def json(self, *, system: str, prompt: str, schema: dict, max_tokens: int = 8000,
                   fake: Any = None, images: list[tuple[str, bytes]] | None = None) -> dict:
        """`images` ((mime type, bytes) pairs) are shown to models that can see; others get the text only."""
        if self.provider == "claude":
            return unpack(await self._claude(system, prompt, schema, max_tokens, images or []))
        if self.provider == "deepseek":
            return unpack(await self._deepseek(system, prompt, schema, max_tokens))
        if self.provider == "fake":
            if self.fake_delay:
                await asyncio.sleep(self.fake_delay)
            return fake() if callable(fake) else (fake or {})
        raise AIError("ai_unavailable", "no AI model is configured", 503)

    async def _claude(self, system: str, prompt: str, schema: dict, max_tokens: int,
                      images: list[tuple[str, bytes]] | None = None) -> dict:
        content: Any = prompt
        if images:
            import base64
            content = [{"type": "image", "source": {"type": "base64", "media_type": mime,
                                                    "data": base64.b64encode(data).decode()}} for mime, data in images]
            content.append({"type": "text", "text": prompt})
        body = {
            "model": self.claude_model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": content}],
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

    # --- the expert lane (round 5–6): a stronger model that thinks first, and may use tools --------------------
    @property
    def agentic(self) -> bool:
        return self.provider == "claude"

    async def agent(self, *, system: str, messages: list[dict], tools: list[dict], run_tool, model: str = "",
                    thinking: int = 6000, max_tokens: int = 16000, max_rounds: int = 12, on_step=None) -> str:
        """Claude as itself: a multi-turn conversation with extended thinking and tools. `run_tool(name, input)`
        returns the tool's text result (awaitable). Returns the final reply text."""
        if self.provider != "claude":
            raise AIError("agent_unsupported", "the expert lane needs Claude", 503)
        msgs = [dict(m) for m in messages]
        headers = {"x-api-key": self.anthropic_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        text = ""
        for _ in range(max_rounds):
            body = {"model": model or self.claude_model, "max_tokens": max_tokens, "system": system, "messages": msgs,
                    "tools": tools}
            if thinking:
                body["thinking"] = {"type": "enabled", "budget_tokens": thinking}
            try:
                data = await self._post("https://api.anthropic.com/v1/messages", body, headers, timeout=max(self.timeout, 600))
            except AIError as e:
                if model and model != self.claude_model and "not_found" in str(e):   # that model is not on this account
                    model = self.claude_model
                    continue
                raise
            content = data.get("content") or []
            text = "\n".join(b.get("text", "") for b in content if b.get("type") == "text").strip() or text
            uses = [b for b in content if b.get("type") == "tool_use"]
            if data.get("stop_reason") != "tool_use" or not uses:
                return text
            msgs.append({"role": "assistant", "content": content})
            results = []
            for u in uses:
                if on_step:
                    await on_step(u["name"], u.get("input") or {})
                try:
                    out = await run_tool(u["name"], u.get("input") or {})
                except Exception as e:  # noqa: BLE001 - the model sees the error and can recover
                    out = f"ERROR: {type(e).__name__}: {e}"
                results.append({"type": "tool_result", "tool_use_id": u["id"], "content": str(out)[:60000]})
            msgs.append({"role": "user", "content": results})
        return text or "（我查了很多轮还没想清楚，请把问题说得再具体一点。）"

    async def think_json(self, *, system: str, prompt: str, schema: dict, model: str = "", thinking: int = 8000,
                         max_tokens: int = 20000, fake: Any = None) -> dict:
        """A considered answer: the model thinks first, then writes JSON (Claude); other providers use json()."""
        if self.provider != "claude":
            return await self.json(system=system, prompt=prompt, schema=schema, max_tokens=min(max_tokens, 8000), fake=fake)
        body = {"model": model or self.claude_model, "max_tokens": max_tokens, "system": system,
                "thinking": {"type": "enabled", "budget_tokens": thinking},
                "messages": [{"role": "user", "content": prompt + "\n\nAfter thinking, reply with ONE JSON object matching this "
                                                               "JSON Schema and nothing else:\n" + json.dumps(schema, ensure_ascii=False)}]}
        headers = {"x-api-key": self.anthropic_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        try:
            data = await self._post("https://api.anthropic.com/v1/messages", body, headers, timeout=max(self.timeout, 600))
        except AIError as e:
            if not (model and model != self.claude_model and "not_found" in str(e)):
                raise
            body["model"] = self.claude_model
            data = await self._post("https://api.anthropic.com/v1/messages", body, headers, timeout=max(self.timeout, 600))
        text = "\n".join(b.get("text", "") for b in data.get("content") or [] if b.get("type") == "text")
        m = re.search(r"\{.*\}", text, re.S)
        try:
            return json.loads(m.group(0)) if m else {}
        except ValueError as exc:
            raise AIError("ai_bad_output", "model returned invalid JSON", 502) from exc

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

    async def _post(self, url: str, body: dict, headers: dict, timeout: float | None = None) -> dict:
        try:
            r = await self.http.post(url, json=body, headers=headers, timeout=timeout or self.timeout)
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
