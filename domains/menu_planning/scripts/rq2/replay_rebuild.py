"""Rebuild the exact prompt (token IDs) vLLM saw for a logged request.
Usage: from replay_rebuild import rebuild_messages, render
"""
import copy, json


def rebuild_messages(request: dict, rename_reasoning=True, parse_args=True,
                     tools_inner=False, none_content=False, drop_reasoning=False):
    """Return (messages, tools) ready for tokenizer.apply_chat_template.
    Defaults = best variant found in T1 (see T1_REPORT.md)."""
    msgs = copy.deepcopy(request["messages"])
    for m in msgs:
        if m["role"] == "assistant":
            if drop_reasoning:
                m.pop("reasoning", None)
            elif rename_reasoning and "reasoning" in m:
                m["reasoning_content"] = m.pop("reasoning")  # vLLM-side rename
            for tc in m.get("tool_calls") or []:
                a = tc["function"].get("arguments")
                if parse_args and isinstance(a, str):
                    tc["function"]["arguments"] = json.loads(a) if a.strip() else {}
            if none_content and m.get("content") == "":
                m["content"] = None
    tools = copy.deepcopy(request.get("tools")) or None
    if tools and tools_inner:
        tools = [t["function"] for t in tools]
    return msgs, tools


def render(request: dict, tokenizer, template_kwargs=None, **kw) -> list:
    msgs, tools = rebuild_messages(request, **kw)
    out = tokenizer.apply_chat_template(msgs, tools=tools, add_generation_prompt=True,
                                        tokenize=True, **(template_kwargs or {}))
    if hasattr(out, "keys"):
        out = out["input_ids"]
    return list(out)


# ---------------------------------------------------------------------------
# Rebuild a request from an Inspect ModelEvent when event.call is None.
# Mirrors inspect_ai.model._openai.openai_chat_message (system_role="system"),
# i.e. what the openai-compatible provider logged for the other calls.
# ---------------------------------------------------------------------------
_REASONING_KEYS = ("reasoning", "reasoning_content", "reasoning_details")


def _assistant_param(m):
    if isinstance(m.content, str):
        content, extra = m.content, {}
    else:
        content, extra = "", {}
        for c in m.content:
            if c.type == "reasoning":
                if str(c.internal) in _REASONING_KEYS:  # key named by .internal, as logged
                    extra[str(c.internal)] = c.reasoning
                else:
                    content = f"{content}\n<think>\n{c.reasoning}\n</think>\n"  # not hit in our logs
            elif c.type == "text":
                content = f"{content}\n{c.text}"  # Inspect prefixes every text block with "\n"
    out = {"role": "assistant", "content": content}
    if m.tool_calls:
        out["tool_calls"] = [
            {"id": tc.id, "type": "function",
             "function": {"name": tc.function, "arguments": json.dumps(tc.arguments)}}
            for tc in m.tool_calls]
    return out | extra


def request_from_event(event, prev_request: dict | None) -> dict:
    """OpenAI-format request for a ModelEvent; tools/tool_choice/etc. copied from
    prev_request (nearest logged request of the same sample)."""
    msgs = []
    for m in event.input:
        if m.role in ("system", "user"):
            msgs.append({"role": m.role, "content": m.content if isinstance(m.content, str) else m.text})
        elif m.role == "assistant":
            msgs.append(_assistant_param(m))
        elif m.role == "tool":
            msgs.append({"role": "tool",
                         "content": f"Error: {m.error.message}" if m.error else m.text,
                         "tool_call_id": str(m.tool_call_id)})
        else:
            raise ValueError(m.role)
    req = {k: copy.deepcopy(v) for k, v in (prev_request or {}).items() if k != "messages"}
    req["messages"] = msgs
    return req
