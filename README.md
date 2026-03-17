# Impact Clarity

A choose-your-own-adventure CLI game for figuring out your path in effective altruism.

Built for people who are deep in EA and feel stuck — not beginners looking for an intro.
Uses Claude to narrate and personalize each branch based on your context.

---

## Quickstart

**Requires:** [uv](https://docs.astral.sh/uv/getting-started/installation/) and an [Anthropic API key](https://console.anthropic.com/settings/keys)

```bash
git clone https://github.com/YOUR_USERNAME/choose-adventure
cd choose-adventure
uv run adventure
```

On first run it will ask for your API key and save it to `~/.config/choose-adventure/key`.

Or set it as an env variable:

```bash
ANTHROPIC_API_KEY=sk-ant-... uv run adventure
```

---

## Controls

| Key | Action |
|-----|--------|
| `1` `2` `3`... | Choose a path |
| `f` | Speak freely — Claude will route you |
| `g` | Show your path map so far |
| `q` | Quit |

---

## How it works

Pre-authored decision tree (14 nodes) covering the most common places people get stuck:
skill/fit doubts, unclear what "enough" means, nuanced EA views, student constraints,
cause area exploration (AI safety + animal welfare), and leaf nodes with concrete reframes.

Claude personalizes the narration at each node using your accumulated context — cause areas,
background, things you've said, and insights from your choices.

---

## Extending

Routes live in `routes/*.yaml`. Each node:

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

Add a new `.yaml` file to `routes/` and it's picked up automatically.

---

## Cost

~$0.10–0.20 per session (Anthropic API, Claude Opus 4.6).
Get a key at [console.anthropic.com](https://console.anthropic.com/settings/keys).
