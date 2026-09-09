"""Deterministic normalization of WeaveBench chat.jsonl into an ordered event list.

Schema observed (inspected before writing; see recoverability_report.md):
  line: {id, parentId, timestamp, type, message?}
  type == "message":
    message.role == "assistant" -> content: [{type: thinking|text|toolCall, ...}]
    message.role == "toolResult" -> {toolCallId, toolName, content:[{type:text|image}], isError}
    message.role == "user"      -> content: [{type: text|image}]
  other types: session | model_change | thinking_level_change | custom

No LLM inference. No semantic matching.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class Event:
    idx: int                      # 0-based position in the tool-call/message stream
    line_no: int                  # 0-based line in chat.jsonl
    kind: str                     # toolCall | toolResult | assistantText | thinking | userText | meta
    role: str = ""
    tool: str = ""                # exec | read | __computer__ | write | ...
    call_id: str = ""
    args: dict = field(default_factory=dict)
    command: str = ""             # exec command / read file_path / computer actions json
    result_text: str = ""         # linked toolResult text (on toolCall events)
    is_error: bool = False
    n_images: int = 0             # images returned by the linked toolResult
    timestamp: str = ""
    text: str = ""                # assistant/user/thinking text

    def searchable(self) -> str:
        """Text a judge quote could have been drawn from, for this event.

        Includes canonical renderings of the tool call, because the judge cites
        tool calls in rendered forms such as "read <path>", "write <path> <content>",
        "edit new_string: <text>" and "toolCall: <code>" rather than verbatim JSON.
        """
        parts = [self.command, self.result_text, self.text]
        a = self.args or {}
        if a:
            parts.append(json.dumps(a, ensure_ascii=False))
        fp = a.get("file_path") or a.get("path") or ""
        if self.tool and fp:
            parts.append(self.tool + " " + str(fp))
        if "content" in a:
            parts.append(self.tool + " " + str(fp) + " " + str(a.get("content", "")))
        if "new_string" in a:
            parts.append(self.tool + " new_string: " + str(a.get("new_string", "")))
        if "old_string" in a:
            parts.append(self.tool + " old_string: " + str(a.get("old_string", "")))
        if self.command:
            parts.append("toolCall: " + str(self.command))
        return chr(10).join(str(x) for x in parts if x)

def _parts_text(content) -> tuple[str, int]:
    """Concatenate text parts; count image parts."""
    if isinstance(content, str):
        return content, 0
    txt, n_img = [], 0
    for p in content or []:
        if not isinstance(p, dict):
            continue
        t = p.get("type")
        if t == "text":
            txt.append(p.get("text", ""))
        elif t == "image":
            n_img += 1
        elif t == "thinking":
            txt.append(p.get("thinking", "") or p.get("text", ""))
    return "\n".join(txt), n_img


def parse_trace(path: str) -> list[Event]:
    lines = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                try:
                    lines.append(json.loads(ln))
                except json.JSONDecodeError:
                    lines.append({"type": "_unparsed"})

    # index toolResults by toolCallId
    results: dict[str, dict] = {}
    for o in lines:
        if o.get("type") == "message" and (o.get("message") or {}).get("role") == "toolResult":
            m = o["message"]
            results[m.get("toolCallId", "")] = m

    events: list[Event] = []
    idx = 0
    for line_no, o in enumerate(lines):
        if o.get("type") != "message":
            continue
        m = o.get("message") or {}
        role = m.get("role", "")
        ts = m.get("timestamp") or o.get("timestamp") or ""
        if role == "assistant":
            for p in m.get("content") or []:
                if not isinstance(p, dict):
                    continue
                if p.get("type") == "toolCall":
                    a = p.get("arguments") or {}
                    if isinstance(a, str):
                        try:
                            a = json.loads(a)
                        except json.JSONDecodeError:
                            a = {"_raw": a}
                    cmd = a.get("command") or a.get("file_path") or a.get("path") or ""
                    if not cmd and "actions" in a:
                        cmd = json.dumps(a["actions"], ensure_ascii=False)
                    if not cmd:
                        cmd = json.dumps(a, ensure_ascii=False)
                    r = results.get(p.get("id", ""))
                    rtxt, n_img = _parts_text(r.get("content")) if r else ("", 0)
                    events.append(Event(
                        idx=idx, line_no=line_no, kind="toolCall", role=role,
                        tool=p.get("name") or p.get("toolName") or "", call_id=p.get("id", ""),
                        args=a if isinstance(a, dict) else {}, command=str(cmd),
                        result_text=rtxt, is_error=bool(r.get("isError")) if r else False,
                        n_images=n_img, timestamp=ts,
                    ))
                    idx += 1
                elif p.get("type") in ("thinking", "text"):
                    t = p.get("thinking") or p.get("text") or ""
                    if t:
                        events.append(Event(idx=idx, line_no=line_no,
                                            kind="thinking" if p["type"] == "thinking" else "assistantText",
                                            role=role, text=t, timestamp=ts))
                        idx += 1
        elif role == "user":
            t, n_img = _parts_text(m.get("content"))
            events.append(Event(idx=idx, line_no=line_no, kind="userText", role=role,
                                text=t, n_images=n_img, timestamp=ts))
            idx += 1
    return events


def tool_calls(events: list[Event]) -> list[Event]:
    return [e for e in events if e.kind == "toolCall"]
