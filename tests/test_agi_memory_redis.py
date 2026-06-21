"""Tests for shared/agi_memory_redis.py using a dict-backed fake Redis client."""

from agi_provider import MemoryInterface, ReasoningStep, create_agi_provider
from shared.agi_memory_redis import RedisAGIMemory, create_redis_agi_memory


class FakeRedisClient:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value: str) -> None:
        self._store[key] = value


def test_redis_memory_satisfies_memory_interface():
    mem = RedisAGIMemory(session_id="t1", client=FakeRedisClient())
    assert isinstance(mem, MemoryInterface)


def test_redis_memory_bounded_history():
    client = FakeRedisClient()
    mem = RedisAGIMemory(session_id="t2", client=client, max_history=3)

    for i in range(5):
        mem.add_message({"role": "user", "content": f"msg-{i}"})

    assert len(mem.conversation_history) == 3
    assert mem.conversation_history[0]["content"] == "msg-2"


def test_redis_memory_retains_system_messages_on_truncation():
    client = FakeRedisClient()
    mem = RedisAGIMemory(session_id="system-cap", client=client, max_history=3)

    mem.add_message({"role": "system", "content": "core instructions"})
    for i in range(4):
        mem.add_message({"role": "user", "content": f"msg-{i}"})

    roles = [m["role"] for m in mem.conversation_history]
    assert roles.count("system") == 1
    assert mem.conversation_history[0]["content"] == "core instructions"
    assert len(mem.conversation_history) == 3


def test_redis_memory_persists_across_instances():
    client = FakeRedisClient()
    mem1 = RedisAGIMemory(session_id="shared", client=client)
    mem1.add_message({"role": "user", "content": "hello redis"})

    mem2 = RedisAGIMemory(session_id="shared", client=client)
    assert len(mem2.conversation_history) == 1
    assert mem2.conversation_history[0]["content"] == "hello redis"


def test_redis_memory_reasoning_chain_cap():
    client = FakeRedisClient()
    mem = RedisAGIMemory(session_id="chains", client=client)
    chain = [ReasoningStep(step_type="analyze", content="step")]

    for _ in range(12):
        mem.add_reasoning_chain(chain)

    assert len(mem.reasoning_chains) == 10


def test_redis_memory_get_relevant_context():
    client = FakeRedisClient()
    mem = RedisAGIMemory(session_id="ctx", client=client)
    mem.add_message({"role": "user", "content": "Explain LoRA"})
    mem.goals.append("finish tests")

    ctx = mem.get_relevant_context("Explain LoRA")
    assert "Recent conversation:" in ctx
    assert "Active goals:" in ctx


def test_redis_memory_learned_patterns_persist():
    client = FakeRedisClient()
    mem = RedisAGIMemory(session_id="patterns", client=client)
    mem.learned_patterns["route_key"] = {
        "agent": "code-specialist", "count": 1}

    mem2 = RedisAGIMemory(session_id="patterns", client=client)
    assert mem2.learned_patterns.get(
        "route_key", {}).get("agent") == "code-specialist"


def test_create_agi_provider_uses_redis_memory(monkeypatch):
    client = FakeRedisClient()
    monkeypatch.setenv("QAI_AGI_MEMORY_BACKEND", "redis")

    def _fake_create(**kwargs):
        return RedisAGIMemory(session_id="provider-test", client=client)

    monkeypatch.setattr(
        "shared.agi_memory_redis.create_redis_agi_memory",
        _fake_create,
    )

    provider, _ = create_agi_provider(verbose=False)
    assert type(provider.context).__name__ == "RedisAGIMemory"

    monkeypatch.delenv("QAI_AGI_MEMORY_BACKEND", raising=False)


def test_create_redis_agi_memory_factory():
    client = FakeRedisClient()
    mem = create_redis_agi_memory(session_id="factory", client=client)
    mem.add_message({"role": "user", "content": "factory test"})
    raw = client.get("agi:factory:state")
    assert raw
    assert "factory test" in raw
