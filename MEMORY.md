---
name: choose-adventure project memory
description: Context about the project, the user, and decisions made
type: project
---

# Project Memory

## Who this is for

User is a student (~6 years into EA), working on side projects alongside school.
Target user and primary designer of the adventure routes.

**EA background:** Direct work-adjacent (ops, comms at EA orgs) + self-directed research.
Applied to top EA orgs, contributed to projects, seriously explored career pivots.
Built: relationships, writing, operations.

**Cause areas:** AI safety/governance and animal welfare.

**Philosophy:** Evolved/nuanced — holds EA loosely, not dogmatically bought in.

**Blocker:** Skill/fit doubts + practical student constraints (time, money).
Has tried the standard paths without landing.

**Tech preferences:** Python + uv. No bloat.

---

## Architecture decisions

- Routes defined in YAML (`routes/*.yaml`) — pre-authored graph, engine picks up all files automatically
- Claude does three things: narrate, commentary, route free responses — all in `src/adventure/claude.py`
- Session context accumulates in `SessionContext` dataclass, serialized to a text block passed in every Claude call
- Claude never sees the graph structure — only narrative text and context
- Graph explorer at end of session uses `rich.tree` + `networkx`

## Model

- Default: `claude-sonnet-4-6` — handles short contextual narration well
- Option: `claude-opus-4-6` — better nuance, worth it for demos or deep sessions
- User chooses at startup with a short honest pitch; Sonnet is default
- Cost: Sonnet ~$0.05/session, Opus ~$0.08/session (session = one full playthrough, ~8-10 nodes)

## API key

- Stored at `~/.config/choose-adventure/key` (outside repo, `chmod 0o600`, masked input)
- Falls back to `ANTHROPIC_API_KEY` env var
- `.env` approach was considered and rejected — `~/.config` is cleaner and already solved it

## Distribution

- GitHub: https://github.com/sacchen/impact-path
- CLI chosen over web (demo this week, users bring their own key)
- Share: `git clone https://github.com/sacchen/impact-path && cd impact-path && uv run adventure`
- Web version is a future option if broader reach is needed

## Running

```bash
uv run adventure
```

First run prompts for API key, saves it, never asks again.

## Extending

- Add new routes: drop a `.yaml` into `routes/` following the same node format
- Add new Claude behaviors: add a function to `claude.py`
- The `claude_hint` field in each node guides narration without being shown to the user
- Swap backends: `from . import claude_cli as llm` for CC subscription (slower, ~8s/call)
