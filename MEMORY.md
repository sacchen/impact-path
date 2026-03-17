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
- Model: `claude-opus-4-6`
- Graph explorer at end of session uses `rich.tree` + `networkx`

## Running

```bash
uv run adventure
```

Requires `ANTHROPIC_API_KEY` in environment.

## Extending

- Add new routes: drop a `.yaml` into `routes/` following the same node format
- Add new Claude behaviors: add a function to `claude.py`
- The `claude_hint` field in each node guides narration without being shown to the user
