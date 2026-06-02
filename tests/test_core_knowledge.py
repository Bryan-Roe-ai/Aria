"""Focused tests for the core knowledge graph package."""

from __future__ import annotations

import json

from core.knowledge.graph import ConceptLinker, KnowledgeGraph, OntologyLoader
from core.memory.store import MemoryStore


def test_knowledge_graph_paths_and_neighbors() -> None:
    graph = KnowledgeGraph()
    graph.add_relationship("alpha", "beta", "links_to")
    graph.add_relationship("beta", "gamma", "links_to")

    assert graph.neighbors("alpha") == ["beta"]
    assert graph.shortest_path("alpha", "gamma") == ["alpha", "beta", "gamma"]
    assert "beta" in graph.find_related("alpha")


def test_knowledge_graph_merges_properties_and_handles_missing_paths() -> None:
    graph = KnowledgeGraph()

    graph.add_entity("planner", {"kind": "runtime"})
    graph.add_entity("planner", {"status": "ready"})

    assert graph.to_dict()["entities"]["planner"] == {
        "kind": "runtime",
        "status": "ready",
    }
    assert graph.shortest_path("planner", "missing") == []


def test_concept_linker_links_recent_events_into_graph() -> None:
    memory = MemoryStore()
    memory.write("goal_created", {"goal": "improve planning"})
    memory.write("task_result", {"output": "inspect context"})

    graph = KnowledgeGraph()
    ConceptLinker(graph, memory).link_recent(10)

    assert "improve planning" in graph.neighbors("goal_created")
    assert "inspect context" in graph.neighbors("task_result")


def test_ontology_loader_applies_entities_and_relationships(tmp_path) -> None:
    ontology_path = tmp_path / "ontology.json"
    ontology_path.write_text(
        json.dumps(
            {
                "entities": [
                    "planner",
                    {"name": "agent", "properties": {"kind": "runtime"}},
                ],
                "relationships": [
                    {
                        "source": "planner",
                        "target": "agent",
                        "relation": "instance_of",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    loader = OntologyLoader()
    graph = KnowledgeGraph()
    loader.apply_to_graph(graph, loader.load(str(ontology_path)))

    assert graph.shortest_path("planner", "agent") == ["planner", "agent"]
