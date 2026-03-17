# Impact Clarity

A choose-your-own-adventure CLI for figuring out your EA impact path.

Built for people who are deep in it and feel stuck — not beginners looking for an intro.
Claude narrates and personalizes each branch based on what you share as you go.

---

## Quickstart

**Requires:** [uv](https://docs.astral.sh/uv/getting-started/installation/) and an [Anthropic API key](https://console.anthropic.com/settings/keys)

```bash
git clone https://github.com/sacchen/impact-path
cd impact-path
uv run adventure
```

On first run it will ask for your API key (saved to `~/.config/choose-adventure/key`, masked input, not committed to git) and which model to use. After that it just runs.

---

## Controls

| Key | Action |
|-----|--------|
| `1` `2` `3`... | Choose a path |
| `f` | Speak freely — Claude routes you |
| `g` | Show your path map |
| `q` | Quit |

---

## Model choice

At startup you'll be asked: **Sonnet** or **Opus**?

- **Sonnet** — handles this well. Short contextual narration is its sweet spot. (~$0.05/session)
- **Opus** — goes deeper on nuance and subtext, worth it if you want to really sit with it or are demoing to someone. (~$0.08/session)

A "session" is one full playthrough — start to a leaf node, roughly 8–10 nodes. Not per message.

---

## How it works

14 pre-authored nodes covering the most common stuck points: skill/fit doubts, unclear what "enough" means, nuanced EA views, student constraints, cause area exploration (AI safety + animal welfare). Claude personalizes the narration at each node using your context — cause areas, background, things you've said, insights from earlier choices.

---

## Extending

Routes live in `routes/*.yaml`. Drop in a new file and it's picked up automatically.

```yaml
- id: my_node
  narrative: |
    Base text Claude personalizes...
  claude_hint: "What Claude should emphasize here."
  choices:
    - label: "A path forward"
      next: next_node_id
    - label: "Something else"
      type: free_response
```
