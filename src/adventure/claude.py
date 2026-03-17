import json
import anthropic

from .config import get_api_key

client: anthropic.Anthropic | None = None
MODEL = "claude-opus-4-6"


def _client() -> anthropic.Anthropic:
    global client
    if client is None:
        client = anthropic.Anthropic(api_key=get_api_key())
    return client

SYSTEM_PROMPT = """You are the narrator of a choose-your-own-adventure game helping someone find
clarity about their impact path in effective altruism.

Your role:
1. Narrate the current moment in a way that feels real and specific to this person
2. Give brief, pointed commentary when they make a choice
3. Help route them when they speak freely

Tone: warm but honest. Not saccharine. Not preachy. Not 'EA career guide' generic.
You're talking to someone who has been in EA for six years — they know the basics.
Speak to the actual complexity of their situation. Reference their specific context
when you have it (cause areas, background, what they've built, what they've tried).

Keep responses SHORT:
- Narrations: 2-4 sentences, personalizing the base narrative to them
- Commentary: 1-2 sentences max, no sycophancy
- Free response routing: return JSON only"""


def narrate(node_narrative: str, claude_hint: str, ctx) -> str:
    """Personalize a node narrative using session context. Streams to stdout."""
    context_str = ctx.to_prompt()

    prompt = f"""Narrate this moment. Personalize it using the player's context.
Keep it to 2-4 sentences. Don't repeat things they already know about themselves.
If you have context about them, use it — make it feel like you're talking to this
specific person, not a generic EA person.

Base narrative:
{node_narrative}

Narrator guidance: {claude_hint or 'None'}

Player context:
{context_str if context_str else 'Just starting — no context yet.'}

Write only the narration. No preamble, no meta-commentary."""

    result = []
    with _client().messages.stream(
        model=MODEL,
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            result.append(text)

    return "".join(result)


def commentary(choice_label: str, ctx) -> str:
    """Brief commentary after a choice is made. Streams to stdout."""
    context_str = ctx.to_prompt()

    prompt = f"""The player just chose: "{choice_label}"

Give a 1-sentence response — acknowledge their choice, add a small observation if useful.
No sycophancy. Don't say "great choice" or "interesting." Just move them forward.

Player context:
{context_str if context_str else 'Just starting.'}

Write only the 1-sentence response."""

    result = []
    with _client().messages.stream(
        model=MODEL,
        max_tokens=80,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            result.append(text)

    return "".join(result)


def route_free_response(user_text: str, available_nodes: list[dict], ctx) -> dict:
    """Route free text to the best node. Returns {node_id, insight, follow_up}."""
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
- "insight": a 1-sentence insight about what they just revealed (for context accumulation)
- "follow_up": a short clarifying question to ask before routing, or null if not needed

Return only valid JSON, nothing else."""

    response = _client().messages.create(
        model=MODEL,
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    # Strip markdown code fences if present
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
    """Extract a key insight from a meaningful choice to accumulate in context."""
    significant = {
        "skill_doubts", "unclear_enough", "nuanced_ea", "adjacent_reframe",
        "tried_standard_path", "clarity_reframe", "skill_gap_real",
    }
    if node_id not in significant:
        return None

    response = _client().messages.create(
        model=MODEL,
        max_tokens=80,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                f'The player chose "{choice_label}" and is now at node "{node_id}".\n\n'
                f"Extract a 1-sentence insight about what this choice reveals about them.\n"
                f"Be specific, not generic. Return only the insight sentence."
            ),
        }],
    )
    return response.content[0].text.strip()
