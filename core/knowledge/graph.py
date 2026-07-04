from __future__ import annotations

import json
from collections import deque
from typing import Any

from core.memory.store import MemoryStore


class KnowledgeGraph:
    def __init__(self) -> None:
        self._entities: dict[str, dict[str, Any]] = {}
        self._edges: dict[str, list[dict[str, Any]]] = {}

    def add_entity(self, name: str, properties: dict[str, Any] | None = None) -> None:
        if not name:
            return
        if name not in self._entities:
            self._entities[name] = properties or {}
            self._edges[name] = []
        elif properties:
            self._entities[name].update(properties)

    def add_relationship(self, source: str, target: str, relation: str, weight: float = 1.0) -> None:
        self.add_entity(source)
        self.add_entity(target)
        self._edges[source].append({"target": target, "relation": relation, "weight": weight})

    def neighbors(self, entity: str) -> list[str]:
        return [edge["target"] for edge in self._edges.get(entity, [])]

    def find_related(self, entity: str, max_depth: int = 2) -> list[str]:
        visited = set()
        queue = deque([(entity, 0)])
        related: list[str] = []
        while queue:
            current, depth = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            if current != entity:
                related.append(current)
            if depth < max_depth:
                for neighbor in self.neighbors(current):
                    if neighbor not in visited:
                        queue.append((neighbor, depth + 1))
        return related

    def shortest_path(self, source: str, target: str) -> list[str]:
        if source not in self._entities or target not in self._entities:
            return []
        if source == target:
            return [source]
        visited = {source}
        queue = deque([[source]])
        while queue:
            path = queue.popleft()
            current = path[-1]
            for neighbor in self.neighbors(current):
                if neighbor == target:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return []

    def to_dict(self) -> dict[str, Any]:
        return {"entities": dict(self._entities), "edges": self._edges}


class ConceptLinker:
    def __init__(self, graph: KnowledgeGraph, memory: MemoryStore) -> None:
        self.graph = graph
        self.memory = memory

    def link_event(self, event: dict[str, Any]) -> None:
        data = event.get("data", {})
        event_type = str(event.get("type", "event"))
        self.graph.add_entity(event_type)

        entity_fields = ["goal", "output", "message", "type"]
        entities_found: list[str] = []
        if isinstance(data, dict):
            for field in entity_fields:
                value = data.get(field)
                if value and isinstance(value, str):
                    self.graph.add_entity(value)
                    entities_found.append(value)

        for entity in entities_found:
            self.graph.add_relationship(event_type, entity, "contains")

    def link_recent(self, n: int = 20) -> None:
        for event in self.memory.last(n):
            self.link_event(event)


class OntologyLoader:
    def load(self, path: str) -> dict[str, Any]:
        with open(path, encoding="utf-8") as handle:
            content = handle.read()
        if path.endswith((".yaml", ".yml")):
            try:
                import yaml

                loaded = yaml.safe_load(content)
                return loaded or {}
            except ImportError:
                pass
        return json.loads(content)

    def apply_to_graph(self, graph: KnowledgeGraph, ontology: dict[str, Any]) -> None:
        for entity in ontology.get("entities", []):
            if isinstance(entity, str):
                graph.add_entity(entity)
            elif isinstance(entity, dict):
                graph.add_entity(entity.get("name", ""), entity.get("properties"))
        for relationship in ontology.get("relationships", []):
            graph.add_relationship(
                relationship["source"],
                relationship["target"],
                relationship["relation"],
                float(relationship.get("weight", 1.0)),
            )
