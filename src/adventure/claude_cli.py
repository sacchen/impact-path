"""
Claude Code CLI backend — alternative to claude.py (API).

Uses `claude -p` so it runs under your CC subscription with no API key needed.
Drop-in replacement: same function signatures as claude.py.

Tradeoffs vs API (claude.py):
  + No API key / no per-token billing (uses CC subscription)
  - ~7-9s per call vs ~1-3s for API (CC infrastructure overhead)
  - Default model is Sonnet 4.6 (use --model opus to override, subject to CC rate limits)
  - Streaming requires parsing NDJSON; no streaming for route_free_response

To swap backends, change the import in engine.py:
  from . import claude_cli as llm   # CC subscription
  from . import claude as llm       # API key
"""

import json
import subprocess


MODEL = "claude-sonnet-4-6"  # default in CC; change to "opus" for stronger narration

SYSTEM_PROMPT = """You are the narrator of a choose-your-own-adventure game helping someone find
clarity about their impact path in effective altruism.

Your role:
1. Narrate the current moment in a way that feels real and specific to this person
2. Give brief, pointed commentary when they make a choice
3. Help route them when they speak freely

Tone: warm but honest. Not saccharine. Not preachy. Not 'EA career guide' generic.
You're talking to someone who has been in EA for six years — they know the basics.
Speak to the actual complexity of their situation. Reference their specific context
when you have it.

Keep responses SHORT:
- Narrations: 2-4 sentences, personalizing the base narrative to them
- Commentary: 1-2 sentences max, no sycophancy
- Free response routing: return JSON only"""


def _stream_call(prompt: str) -> str:
    """Run claude -p with stream-json, print tokens as they arrive, return full text."""
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json",
        "--include-partial-messages",
        "--verbose",
        "--no-session-persistence",
        "--system-prompt", SYSTEM_PROMPT,
        "--model", MODEL,
        "--tools", "",  # disable all tools — pure text generation
    ]

    result = []
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Stream text deltas token by token
        if (
            obj.get("type") == "stream_event"
            and obj.get("event", {}).get("type") == "content_block_delta"
            and obj["event"].get("delta", {}).get("type") == "text_delta"
        ):
            token = obj["event"]["delta"]["text"]
            print(token, end="", flush=True)
            result.append(token)

        # Final result — stop reading
        if obj.get("type") == "result":
            break

    proc.wait()
    return "".join(result)


def _text_call(prompt: str) -> str:
    """Run claude -p with text output. No streaming. Used for JSON responses."""
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "text",
        "--no-session-persistence",
        "--system-prompt", SYSTEM_PROMPT,
        "--model", MODEL,
        "--tools", "",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def narrate(node_narrative: str, claude_hint: str, ctx) -> str:
    context_str = ctx.to_prompt()

    prompt = f"""Narrate this moment. Personalize it using the player's context.
Keep it to 2-4 sentences. Don't repeat things they already know about themselves.

Base narrative:
{node_narrative}

Narrator guidance: {claude_hint or 'None'}

Player context:
{context_str if context_str else 'Just starting — no context yet.'}

Write only the narration. No preamble."""

    return _stream_call(prompt)


def commentary(choice_label: str, ctx) -> str:
    context_str = ctx.to_prompt()

    prompt = f"""The player just chose: "{choice_label}"

Give a 1-sentence response. No sycophancy. Just move them forward.

Player context:
{context_str if context_str else 'Just starting.'}

Write only the 1-sentence response."""

    return _stream_call(prompt)


def route_free_response(user_text: str, available_nodes: list[dict], ctx) -> dict:
    context_str = ctx.to_prompt()

    node_options = "\n".join(
        f"- {n['id']}: {n.get('narrative', '')[:100].strip()}..."
        for n in available_nodes
    )

    prompt = f"""The player said: "{user_text}"

Available next nodes:
{node_options}

Player context:
{context_str if context_str else 'Just starting.'}

Return JSON with exactly these fields:
- "node_id": the best matching node id from the list above
- "insight": a 1-sentence insight about what they just revealed
- "follow_up": a short clarifying question to ask before routing, or null

Return only valid JSON, nothing else."""

    text = _text_call(prompt)

    # Strip markdown fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "node_id": available_nodes[0]["id"] if available_nodes else "start",
            "insight": user_text[:120],
            "follow_up": None,
        }


def extract_insight(node_id: str, choice_label: str, ctx) -> str | None:
    significant = {
        "skill_doubts", "unclear_enough", "nuanced_ea", "adjacent_reframe",
        "tried_standard_path", "clarity_reframe", "skill_gap_real",
    }
    if node_id not in significant:
        return None

    prompt = (
        f'The player chose "{choice_label}" and is now at node "{node_id}".\n\n'
        f"Extract a 1-sentence insight about what this choice reveals about them.\n"
        f"Be specific, not generic. Return only the insight sentence."
    )

    return _text_call(prompt)
