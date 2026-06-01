"""Tests for the core knowledge graph (core/knowledge/graph.py)."""

from __future__ import annotations

import json

from core.knowledge.graph import ConceptLinker, KnowledgeGraph, OntologyLoader
from core.memory.store import MemoryStore


# --------------------------------------------------------------------------- #
# KnowledgeGraph
# --------------------------------------------------------------------------- #
def test_add_entity_ignores_empty_name():
    g = KnowledgeGraph()
    g.add_entity("")
    assert g.to_dict()["entities"] == {}


def test_add_entity_and_update_properties():
    g = KnowledgeGraph()
    g.add_entity("a", {"x": 1})
    g.add_entity("a", {"y": 2})  # merges into existing
    assert g.to_dict()["entities"]["a"] == {"x": 1, "y": 2}


def test_add_relationship_auto_creates_entities():
    g = KnowledgeGraph()
    g.add_relationship("a", "b", "knows", weight=2.0)
    entities = g.to_dict()["entities"]
    assert "a" in entities and "b" in entities
    assert g.neighbors("a") == ["b"]
    assert g.to_dict()["edges"]["a"][0]["weight"] == 2.0


def test_neighbors_of_unknown_is_empty():
    assert KnowledgeGraph().neighbors("nope") == []


def test_find_related_respects_max_depth():
    g = KnowledgeGraph()
    g.add_relationship("a", "b", "r")
    g.add_relationship("b", "c", "r")
    g.add_relationship("c", "d", "r")
    related = g.find_related("a", max_depth=2)
    assert "b" in related and "c" in related
    assert "d" not in related  # beyond depth 2
    assert "a" not in related  # excludes the origin


def test_shortest_path_same_node():
    g = KnowledgeGraph()
    g.add_entity("a")
    assert g.shortest_path("a", "a") == ["a"]


def test_shortest_path_missing_node():
    g = KnowledgeGraph()
    g.add_entity("a")
    assert g.shortest_path("a", "z") == []


def test_shortest_path_finds_route():
    g = KnowledgeGraph()
    g.add_relationship("a", "b", "r")
    g.add_relationship("b", "c", "r")
    assert g.shortest_path("a", "c") == ["a", "b", "c"]


def test_shortest_path_no_route_returns_empty():
    g = KnowledgeGraph()
    g.add_entity("a")
    g.add_entity("b")
    g.add_relationship("a", "x", "r")
    assert g.shortest_path("a", "b") == []


# --------------------------------------------------------------------------- #
# ConceptLinker
# --------------------------------------------------------------------------- #
def test_concept_linker_links_event_fields():
    g = KnowledgeGraph()
    linker = ConceptLinker(g, MemoryStore())
    linker.link_event({"type": "plan", "data": {"goal": "win", "output": "ok"}})

    assert "plan" in g.to_dict()["entities"]
    assert "win" in g.neighbors("plan")
    assert "ok" in g.neighbors("plan")


def test_concept_linker_ignores_non_string_fields():
    g = KnowledgeGraph()
    linker = ConceptLinker(g, MemoryStore())
    linker.link_event({"type": "metric", "data": {"goal": 42}})
    assert g.neighbors("metric") == []


def test_concept_linker_link_recent_reads_memory():
    memory = MemoryStore()
    memory.write("plan", {"goal": "ship"})
    g = KnowledgeGraph()
    ConceptLinker(g, memory).link_recent(n=5)
    assert "ship" in g.neighbors("plan")


# --------------------------------------------------------------------------- #
# OntologyLoader
# --------------------------------------------------------------------------- #
def test_ontology_loader_reads_json(tmp_path):
    path = tmp_path / "onto.json"
    path.write_text(json.dumps({"entities": ["a", "b"]}), encoding="utf-8")
    assert OntologyLoader().load(str(path)) == {"entities": ["a", "b"]}


def test_ontology_apply_to_graph_string_and_dict_entities():
    g = KnowledgeGraph()
    ontology = {
        "entities": ["a", {"name": "b", "properties": {"k": 1}}, {"name": ""}],
        "relationships": [{"source": "a", "target": "b", "relation": "rel", "weight": 3}],
    }
    OntologyLoader().apply_to_graph(g, ontology)
    entities = g.to_dict()["entities"]
    assert "a" in entities
    assert entities["b"] == {"k": 1}
    assert g.neighbors("a") == ["b"]
    assert g.to_dict()["edges"]["a"][0]["weight"] == 3.0


def test_ontology_loader_reads_yaml_or_falls_back(tmp_path):
    # Works whether or not PyYAML is installed: valid JSON is valid YAML.
    path = tmp_path / "onto.yaml"
    path.write_text('{"entities": ["x"]}', encoding="utf-8")
    loaded = OntologyLoader().load(str(path))
    assert loaded == {"entities": ["x"]}
