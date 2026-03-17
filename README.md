# Impact Clarity

A choose-your-own-adventure CLI for people who've been seriously in EA for years and still feel like something's unresolved.

Not for newcomers. Not a career guide. Built for the person who knows the framework, has tried the paths, and is still figuring out what's actually true for them — whether that's navigating the prestige hierarchy, holding EA more loosely, finding their footing in AI safety or animal welfare or governance, or just not knowing what move to make next.

Claude narrates and personalizes each branch based on what you share as you go.

---

## Who this is for

People across the EA and adjacent landscape who've been at it for a while and feel something unresolved — whatever flavor that takes:

- The person who's applied to orgs, done the fellowships, and still hasn't landed
- The person doing ops or comms or writing who wonders if it counts
- The person who's drifted post-EA but still cares about the underlying goals
- The person deep in suffering-focused ethics, s-risks, formal decision theory
- The person tracking AI governance, great power conflict, coordination problems
- The person who found their way here through prediction markets or postrat Twitter
- The person who holds EA loosely and isn't sure what framework fits better

Common thread: you know the landscape, you've thought about it seriously, and the standard frameworks aren't fully answering your actual question.

---

## Quickstart

**Requires:** [uv](https://docs.astral.sh/uv/getting-started/installation/) and an [Anthropic API key](https://console.anthropic.com/settings/keys)

```bash
git clone https://github.com/sacchen/impact-path
cd impact-path
uv run adventure
```

First run asks for your API key (saved to `~/.config/choose-adventure/key`, masked input, never committed) and which model to use. After that it just runs.

---

## Controls

Type a number to choose a path, or just type what's on your mind — Claude will route you.

| Input | Action |
|-------|--------|
| `1` `2` `3`... | Choose a path |
| anything else | Speak freely — Claude routes you |
| `g` | Show your path so far |
| `q` | Quit |

---

## Model choice

At startup: **Sonnet** or **Opus**?

- **Sonnet** — handles this well. Short contextual narration is its sweet spot. (~$0.05/session)
- **Opus** — goes deeper on nuance and subtext, worth it for demos or when you want to really sit with it. (~$0.08/session)

A "session" is one full playthrough — start to a leaf node, roughly 8–10 nodes. Not per message.

---

## How it works

Pre-authored nodes covering real stuck points: skill and fit doubts, the comparison trap, adjacent work that doesn't feel like enough, unclear what "enough" even means, student constraints, cause area uncertainty, the post-EA question. Claude personalizes narration at each node using your context — what you've built, what you've tried, what you said earlier in the session.

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
