"""Agent registry for the lightweight Aria core runtime."""

from __future__ import annotations

from typing import Dict, List, Optional

from core.agent import BaseAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        if not getattr(agent, "name", "").strip():
            raise ValueError("Registered agents must define a non-empty name.")
        if agent.name in self._agents:
            raise ValueError(f"Agent already registered: {agent.name}")
        self._agents[agent.name] = agent

    def get(self, name: str) -> Optional[BaseAgent]:
        return self._agents.get(name)

    def get_agents(self) -> List[BaseAgent]:
        return list(self._agents.values())

    def names(self) -> List[str]:
        return list(self._agents.keys())
