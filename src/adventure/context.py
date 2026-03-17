from dataclasses import dataclass, field


@dataclass
class SessionContext:
    cause_areas: list[str] = field(default_factory=list)
    background: list[str] = field(default_factory=list)
    stated_blocker: str = ""
    visited_nodes: list[str] = field(default_factory=list)
    free_responses: list[str] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    character_answers: dict = field(default_factory=dict)

    def to_prompt(self) -> str:
        parts = []
        if self.character_answers:
            parts.append("Player context:")
            for k, v in self.character_answers.items():
                parts.append(f"  {k}: {v}")
        if self.cause_areas:
            parts.append(f"Cause areas they care about: {', '.join(self.cause_areas)}")
        if self.stated_blocker:
            parts.append(f"Stated blocker: {self.stated_blocker}")
        if self.free_responses:
            parts.append("Things they've said in their own words:")
            for r in self.free_responses[-3:]:
                parts.append(f"  - {r}")
        if self.insights:
            parts.append("Key insights accumulated so far:")
            for i in self.insights[-5:]:
                parts.append(f"  - {i}")
        if self.visited_nodes:
            parts.append(f"Path so far: {' → '.join(self.visited_nodes[-5:])}")
        return "\n".join(parts)
