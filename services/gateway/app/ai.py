"""Model gateway: one place that talks to language models.

Providers: Claude (Anthropic API), DeepSeek (OpenAI-compatible API, registered for use in
mainland China) and a deterministic `fake` provider used by tests and offline demos.
Every call asks for JSON that matches a schema, so callers get structured data back.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any

import httpx

from .moodle import EngineError

log = logging.getLogger("wenquest.ai")


class AIError(EngineError):
    pass


PLAIN = {
    "ai_timeout": "模型这次想得太久，超时了",
    "ai_busy": "模型这会儿太忙",
    "ai_unreachable": "暂时连不上模型服务",
    "ai_key_invalid": "模型的密钥不对，请管理员检查设置",
    "ai_unavailable": "还没有配置模型",
    "ai_bad_output": "模型这次的回答不完整",
    "ai_error": "模型服务这次返回了错误",
    "agent_unsupported": "当前的模型不支持这种工作方式",
}


def plain(code: str) -> str:
    """A teacher-facing sentence for an error code (round 31: no raw codes on screen)."""
    return PLAIN.get(code or "", "出了点问题")


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


_NEW = re.compile(r"claude-(?:opus|sonnet|haiku|fable|mythos)-(\d+)(?:-(\d+))?")


def model_rules(model: str) -> dict:
    """What a Claude model accepts (round 31, step 0). Claude 5-generation models reject the manual thinking budget
    (`thinking.type = enabled` + `budget_tokens`) and take adaptive thinking with `output_config.effort`; the 5.5 models
    (and later) also reject a forced `tool_choice`. Older models keep the old request shape."""
    m = _NEW.search(model or "")
    if not m:
        return {"adaptive": False, "forced_tool": True}
    major, minor = int(m.group(1)), int(m.group(2) or 0)
    # a long date suffix (e.g. -20251001) is not a minor version
    if minor > 99:
        minor = 0
    adaptive = major >= 5
    forced = not (major > 5 or (major == 5 and minor >= 5))
    return {"adaptive": adaptive, "forced_tool": forced}


def thinking_fields(model: str, budget: int, effort: str = "high") -> dict:
    """The request fields that turn thinking on for this model."""
    if not budget:
        return {}
    if model_rules(model)["adaptive"]:
        return {"thinking": {"type": "adaptive"}, "output_config": {"effort": effort}}
    return {"thinking": {"type": "enabled", "budget_tokens": budget}}


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
        forced = model_rules(self.claude_model)["forced_tool"]
        body = {
            "model": self.claude_model,
            "max_tokens": max_tokens,
            "system": system if forced else system + "\n\nAlways answer by calling the `output` tool exactly once.",
            "messages": [{"role": "user", "content": content}],
            "tools": [{"name": "output", "description": "Return the result.", "input_schema": schema}],
            "tool_choice": {"type": "tool", "name": "output"} if forced else {"type": "auto"},
        }
        headers = {"x-api-key": self.anthropic_key, "anthropic-version": "2023-06-01",
                   "content-type": "application/json"}
        data: dict = {}
        for attempt in range(3):
            # a long answer is streamed: a plain request would hit the read timeout while the model is still writing
            try:
                if body["max_tokens"] > 8000:
                    data = await self._stream("https://api.anthropic.com/v1/messages", body, headers, lambda _t: None,
                                              timeout=max(self.timeout, 900))
                else:
                    data = await self._post("https://api.anthropic.com/v1/messages", body, headers)
            except AIError as e:
                if attempt and e.code == "ai_error" and "max_tokens" in str(e):   # more room than this model allows
                    break
                raise
            truncated = data.get("stop_reason") == "max_tokens"
            for block in data.get("content", []):
                if block.get("type") == "tool_use" and not truncated:
                    return block.get("input") or {}
            if truncated and body["max_tokens"] < 64000:   # a big job ran out of room: again, with more room
                body["max_tokens"] = min(64000, body["max_tokens"] * 2)
                continue
            if not forced:   # the model may have answered in text
                text = "\n".join(b.get("text", "") for b in data.get("content") or [] if b.get("type") == "text")
                m = re.search(r"\{.*\}", text, re.S)
                if m:
                    try:
                        return json.loads(m.group(0))
                    except ValueError:
                        pass
            break
        log.warning("claude gave no structured output: model=%s stop=%s max_tokens=%s usage=%s blocks=%s", body["model"],
                    data.get("stop_reason"), body["max_tokens"], data.get("usage"), [b.get("type") for b in data.get("content") or []])
        raise AIError("ai_bad_output", f"model returned no structured output (stop: {data.get('stop_reason')})", 502)

    # --- the expert lane (round 5–6): a stronger model that thinks first, and may use tools --------------------
    @property
    def agentic(self) -> bool:
        return self.provider == "claude"

    async def agent(self, *, system: str, messages: list[dict], tools: list[dict], run_tool, model: str = "",
                    thinking: int = 6000, max_tokens: int = 16000, max_rounds: int = 12, on_step=None,
                    on_text=None, cancelled=None) -> str:
        """Claude as itself: a multi-turn conversation with extended thinking and tools. `run_tool(name, input)`
        returns the tool's text result (awaitable). Returns the final reply text."""
        if self.provider != "claude":
            raise AIError("agent_unsupported", "the expert lane needs Claude", 503)
        msgs = [dict(m) for m in messages]
        headers = {"x-api-key": self.anthropic_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        text = ""
        for _ in range(max_rounds):
            if cancelled and cancelled():
                return (text + "\n\n" if text else "") + "（已按你的要求停下。）"
            use = model or self.claude_model
            body = {"model": use, "max_tokens": max_tokens, "system": system, "messages": msgs,
                    "tools": tools, **thinking_fields(use, thinking)}
            try:
                if on_text:
                    data = await self._stream("https://api.anthropic.com/v1/messages", body, headers, on_text, text,
                                               timeout=max(self.timeout, 600))
                else:
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
                **thinking_fields(model or self.claude_model, thinking),
                "messages": [{"role": "user", "content": prompt + "\n\nAfter thinking, reply with ONE JSON object matching this "
                                                               "JSON Schema and nothing else:\n" + json.dumps(schema, ensure_ascii=False)}]}
        headers = {"x-api-key": self.anthropic_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        try:
            data = await self._post("https://api.anthropic.com/v1/messages", body, headers, timeout=max(self.timeout, 600))
        except AIError as e:
            if not (model and model != self.claude_model and "not_found" in str(e)):
                raise
            body["model"] = self.claude_model
            body.pop("thinking", None)
            body.pop("output_config", None)
            body.update(thinking_fields(self.claude_model, thinking))
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

    async def _stream(self, url: str, body: dict, headers: dict, on_text, before: str = "", timeout: float | None = None) -> dict:
        """Streaming Messages call (round 31): text deltas go to `on_text` as they arrive; returns the same shape as a
        plain call ({content, stop_reason}). A server that answers with plain JSON (tests) is accepted too."""
        body = {**body, "stream": True}
        blocks: list[dict] = []
        partial: dict[int, str] = {}
        stop = None
        shown = (before + "\n\n") if before else ""
        try:
            async with self.http.stream("POST", url, json=body, headers=headers, timeout=timeout or self.timeout) as r:
                if r.status_code >= 400:
                    await r.aread()
                    self._check(r)
                if "text/event-stream" not in r.headers.get("content-type", ""):
                    await r.aread()
                    data = r.json()
                    t = "\n".join(b.get("text", "") for b in data.get("content") or [] if b.get("type") == "text")
                    if t:
                        on_text(shown + t)
                    return data
                event = ""
                async for line in r.aiter_lines():
                    if line.startswith("event:"):
                        event = line[6:].strip()
                        continue
                    if not line.startswith("data:"):
                        continue
                    try:
                        d = json.loads(line[5:].strip())
                    except ValueError:
                        continue
                    kind = d.get("type") or event
                    if kind == "content_block_start":
                        b = dict(d.get("content_block") or {})
                        if b.get("type") == "tool_use":
                            b["input"] = {}
                        blocks.append(b)
                    elif kind == "content_block_delta" and blocks:
                        i = d.get("index", len(blocks) - 1)
                        b = blocks[i] if i < len(blocks) else blocks[-1]
                        dl = d.get("delta") or {}
                        dt = dl.get("type")
                        if dt == "text_delta":
                            b["text"] = b.get("text", "") + dl.get("text", "")
                            on_text(shown + "\n".join(x.get("text", "") for x in blocks if x.get("type") == "text"))
                        elif dt == "thinking_delta":
                            b["thinking"] = b.get("thinking", "") + dl.get("thinking", "")
                        elif dt == "signature_delta":
                            b["signature"] = dl.get("signature", "")
                        elif dt == "input_json_delta":
                            partial[i] = partial.get(i, "") + dl.get("partial_json", "")
                    elif kind == "content_block_stop":
                        i = d.get("index", len(blocks) - 1)
                        if i in partial and i < len(blocks):
                            try:
                                blocks[i]["input"] = json.loads(partial[i] or "{}")
                            except ValueError:
                                blocks[i]["input"] = {}
                    elif kind == "message_delta":
                        stop = (d.get("delta") or {}).get("stop_reason") or stop
                    elif kind == "error":
                        raise AIError("ai_error", f"model stream error: {json.dumps(d)[:300]}", 502)
        except httpx.TimeoutException as exc:
            raise AIError("ai_timeout", "the model took too long", 504) from exc
        except httpx.HTTPError as exc:
            raise AIError("ai_unreachable", str(exc), 503) from exc
        for b in blocks:   # text blocks carry citations etc. we do not need back
            if b.get("type") == "text":
                b.pop("citations", None)
        return {"content": blocks, "stop_reason": stop}

    def _check(self, r) -> None:
        if r.status_code == 429:
            raise AIError("ai_busy", "rate limited", 429)
        if r.status_code in (401, 403):
            raise AIError("ai_key_invalid", "the API key was rejected", 503)
        if r.status_code >= 400:
            raise AIError("ai_error", f"model API error {r.status_code}: {r.text[:300]}", 502)

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
