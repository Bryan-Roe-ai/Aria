"""Tests for core.cycle_observer and AriaRunner integration."""

from __future__ import annotations

import pytest

from core.bus import AgentBus
from core.cycle_observer import CycleObserver
from core.memory.store import MemoryStore


def _make_observer():
    bus = AgentBus()
    mem = MemoryStore()
    obs = CycleObserver(bus, mem)
    started, completed, failed = [], [], []
    bus.subscribe(CycleObserver.TOPIC_STARTED, started.append)
    bus.subscribe(CycleObserver.TOPIC_COMPLETED, completed.append)
    bus.subscribe(CycleObserver.TOPIC_FAILED, failed.append)
    return obs, started, completed, failed


class TestCycleObserverInitialState:
    def test_all_counters_start_at_zero(self):
        obs, *_ = _make_observer()
        s = obs.stats()
        assert s["total_cycles"] == 0
        assert s["successful_cycles"] == 0
        assert s["failed_cycles"] == 0
        assert s["last_duration_s"] == 0.0
        assert s["cumulative_steps_executed"] == 0
        assert s["cumulative_steps_skipped"] == 0
        assert s["success_rate"] == 0.0


class TestCycleObserverSuccessPath:
    def test_successful_cycle_increments_counters(self):
        obs, _, completed, failed = _make_observer()
        with obs.cycle() as ctx:
            ctx.set_summary({"executed_steps": 3, "skipped_steps": 1, "failed_steps": 0, "goal": "test"})
        s = obs.stats()
        assert s["total_cycles"] == 1
        assert s["successful_cycles"] == 1
        assert s["failed_cycles"] == 0
        assert s["cumulative_steps_executed"] == 3
        assert s["cumulative_steps_skipped"] == 1
        assert s["success_rate"] == 1.0
        assert len(completed) == 1
        assert len(failed) == 0

    def test_completed_event_carries_expected_keys(self):
        obs, _, completed, _ = _make_observer()
        with obs.cycle() as ctx:
            ctx.set_summary({"executed_steps": 2, "skipped_steps": 0, "failed_steps": 1, "goal": "g"})
        event = completed[0]
        assert event["executed_steps"] == 2
        assert event["failed_steps"] == 1
        assert event["goal"] == "g"
        assert "duration_s" in event
        assert event["total_cycles"] == 1

    def test_started_event_emitted_before_completed(self):
        obs, started, completed, _ = _make_observer()
        with obs.cycle():
            pass
        assert len(started) == 1
        assert len(completed) == 1
        assert "cycle_index" in started[0]
        assert "timestamp" in started[0]

    def test_multiple_cycles_accumulate(self):
        obs, _, completed, _ = _make_observer()
        for i in range(3):
            with obs.cycle() as ctx:
                ctx.set_summary({"executed_steps": i + 1, "skipped_steps": 0, "failed_steps": 0})
        s = obs.stats()
        assert s["total_cycles"] == 3
        assert s["successful_cycles"] == 3
        assert s["cumulative_steps_executed"] == 1 + 2 + 3
        assert len(completed) == 3

    def test_last_duration_updated_after_cycle(self):
        obs, *_ = _make_observer()
        with obs.cycle():
            pass
        assert obs.last_duration_s > 0.0

    def test_no_summary_does_not_crash(self):
        obs, _, completed, _ = _make_observer()
        with obs.cycle():
            pass
        assert obs.successful_cycles == 1
        assert completed[0]["executed_steps"] == 0


class TestCycleObserverFailurePath:
    def test_exception_triggers_failed_event(self):
        obs, _, completed, failed = _make_observer()
        with pytest.raises(RuntimeError, match="boom"):
            with obs.cycle():
                raise RuntimeError("boom")
        s = obs.stats()
        assert s["total_cycles"] == 1
        assert s["failed_cycles"] == 1
        assert s["successful_cycles"] == 0
        assert len(failed) == 1
        assert len(completed) == 0

    def test_failed_event_contains_exception_info(self):
        obs, _, _, failed = _make_observer()
        with pytest.raises(ValueError):
            with obs.cycle():
                raise ValueError("bad value")
        event = failed[0]
        assert event["exception_type"] == "ValueError"
        assert "bad" in event["error"]
        assert "duration_s" in event

    def test_success_rate_after_mixed_cycles(self):
        obs, *_ = _make_observer()
        with obs.cycle():
            pass
        with pytest.raises(RuntimeError):
            with obs.cycle():
                raise RuntimeError("x")
        s = obs.stats()
        assert s["total_cycles"] == 2
        assert s["successful_cycles"] == 1
        assert s["failed_cycles"] == 1
        assert s["success_rate"] == 0.5

    def test_exception_is_reraised(self):
        obs, *_ = _make_observer()
        with pytest.raises(ZeroDivisionError):
            with obs.cycle():
                _ = 1 / 0

    def test_failed_cycle_written_to_memory(self):
        bus = AgentBus()
        mem = MemoryStore()
        obs = CycleObserver(bus, mem)
        with pytest.raises(RuntimeError):
            with obs.cycle():
                raise RuntimeError("mem test")
        events = list(mem.query(event_type="cycle_failure"))
        assert len(events) == 1
        assert events[0]["data"]["exception_type"] == "RuntimeError"


class TestCycleObserverMemoryWrites:
    def test_successful_cycle_written_to_memory(self):
        bus = AgentBus()
        mem = MemoryStore()
        obs = CycleObserver(bus, mem)
        with obs.cycle() as ctx:
            ctx.set_summary({"executed_steps": 2, "skipped_steps": 0, "failed_steps": 0, "goal": "g"})
        metrics = list(mem.query(event_type="cycle_metrics"))
        assert len(metrics) == 1
        assert metrics[0]["data"]["executed_steps"] == 2


class TestAriaRunnerObserverIntegration:
    def test_runner_has_observer(self):
        from core.runner import AriaRunner

        r = AriaRunner()
        assert isinstance(r.observer, CycleObserver)

    def test_run_once_increments_observer(self):
        from core.runner import AriaRunner

        r = AriaRunner()
        assert r.observer.total_cycles == 0
        r.run_once()
        assert r.observer.total_cycles == 1
        assert r.observer.successful_cycles == 1

    def test_run_once_publishes_cycle_events(self):
        from core.runner import AriaRunner

        completed_events = []
        r = AriaRunner()
        r.bus.subscribe(CycleObserver.TOPIC_COMPLETED, completed_events.append)
        r.run_once()
        assert len(completed_events) == 1
        event = completed_events[0]
        assert "duration_s" in event
        assert event["successful_cycles"] == 1

    def test_observer_stats_after_run_once(self):
        from core.runner import AriaRunner

        r = AriaRunner()
        r.run_once()
        s = r.observer.stats()
        assert s["total_cycles"] == 1
        assert s["success_rate"] == 1.0
        assert s["last_duration_s"] >= 0.0


# ---------------------------------------------------------------------------
# Slow-cycle threshold tests
# ---------------------------------------------------------------------------


class TestCycleObserverSlowThreshold:
    def test_slow_cycle_event_emitted_when_threshold_exceeded(self):
        bus = AgentBus()
        mem = MemoryStore()
        # threshold=0 means any cycle duration > 0 seconds triggers the alert
        obs = CycleObserver(bus, mem, slow_cycle_threshold_s=0.0)
        slow_events = []
        bus.subscribe(CycleObserver.TOPIC_SLOW, slow_events.append)

        with obs.cycle() as ctx:
            ctx.set_summary({"executed_steps": 1, "skipped_steps": 0, "failed_steps": 0, "goal": "test"})

        assert len(slow_events) == 1
        event = slow_events[0]
        assert "duration_s" in event
        assert event["threshold_s"] == 0.0
        assert obs.slow_cycles == 1

    def test_slow_cycle_event_not_emitted_when_threshold_not_exceeded(self):
        bus = AgentBus()
        mem = MemoryStore()
        # threshold=1000 seconds, so a fast cycle should never trigger
        obs = CycleObserver(bus, mem, slow_cycle_threshold_s=1000.0)
        slow_events = []
        bus.subscribe(CycleObserver.TOPIC_SLOW, slow_events.append)

        with obs.cycle():
            pass

        assert len(slow_events) == 0
        assert obs.slow_cycles == 0

    def test_slow_cycle_event_not_emitted_when_no_threshold(self):
        bus = AgentBus()
        mem = MemoryStore()
        obs = CycleObserver(bus, mem, slow_cycle_threshold_s=None)
        slow_events = []
        bus.subscribe(CycleObserver.TOPIC_SLOW, slow_events.append)

        with obs.cycle():
            pass

        assert len(slow_events) == 0
        assert obs.slow_cycles == 0

    def test_slow_cycles_counter_increments_per_slow_cycle(self):
        bus = AgentBus()
        mem = MemoryStore()
        obs = CycleObserver(bus, mem, slow_cycle_threshold_s=0.0)

        for _ in range(3):
            with obs.cycle():
                pass

        assert obs.slow_cycles == 3
        assert obs.successful_cycles == 3

    def test_slow_cycle_written_to_memory(self):
        bus = AgentBus()
        mem = MemoryStore()
        obs = CycleObserver(bus, mem, slow_cycle_threshold_s=0.0)

        with obs.cycle() as ctx:
            ctx.set_summary({"goal": "mem-test", "executed_steps": 0, "skipped_steps": 0, "failed_steps": 0})

        slow_records = list(mem.query(event_type="cycle_slow"))
        assert len(slow_records) == 1
        assert slow_records[0]["data"]["goal"] == "mem-test"

    def test_failed_cycle_does_not_increment_slow_counter(self):
        bus = AgentBus()
        mem = MemoryStore()
        obs = CycleObserver(bus, mem, slow_cycle_threshold_s=0.0)

        with pytest.raises(RuntimeError):
            with obs.cycle():
                raise RuntimeError("failure")

        assert obs.slow_cycles == 0
        assert obs.failed_cycles == 1

    def test_stats_includes_slow_cycles(self):
        bus = AgentBus()
        mem = MemoryStore()
        obs = CycleObserver(bus, mem, slow_cycle_threshold_s=0.0)

        with obs.cycle():
            pass

        s = obs.stats()
        assert "slow_cycles" in s
        assert s["slow_cycles"] == 1
