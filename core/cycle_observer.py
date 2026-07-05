"""
Aria Cycle Observer

Tracks per-cycle metrics (timing, step counts, failures) for AriaRunner.
Publishes structured summaries to the AgentBus on each cycle start/end/fail.

Topics published:
  "cycle.started"   -- emitted when a new autonomous cycle begins.
  "cycle.completed" -- emitted at the end of a successful cycle.
  "cycle.failed"    -- emitted when an unhandled exception kills a cycle.
  "cycle.slow"      -- emitted when a successful cycle exceeds the budget
                       configured via slow_cycle_threshold_s (default: None,
                       meaning no alerting).
"""
from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.bus import AgentBus
    from core.memory.store import MemoryStore


class CycleObserver:
    """Lightweight observer wrapping an autonomous runner cycle.

    Usage (via context manager)::

        with observer.cycle() as obs:
            result = _autonomous_cycle_body()
            obs.set_summary(result)

    Parameters:
        bus: AgentBus for publishing structured events.
        memory: MemoryStore for persisting cycle metrics.
        slow_cycle_threshold_s: Optional float.  When set, any successful cycle
            that takes longer than this many seconds emits a ``cycle.slow``
            warning event to the bus and writes a ``cycle_slow`` memory event.
            Default: ``None`` (no slow-cycle alerting).

    Attributes:
        total_cycles: Total completed cycles (success + failure).
        successful_cycles: Cycles that completed without exception.
        failed_cycles: Cycles that raised an unhandled exception.
        slow_cycles: Successful cycles that exceeded the slow threshold.
        last_duration_s: Wall-clock seconds of the most recent cycle.
        cumulative_steps_executed: Total plan steps executed across all cycles.
        cumulative_steps_skipped: Total plan steps skipped across all cycles.
    """

    TOPIC_STARTED = "cycle.started"
    TOPIC_COMPLETED = "cycle.completed"
    TOPIC_FAILED = "cycle.failed"
    TOPIC_SLOW = "cycle.slow"

    def __init__(
        self,
        bus: "AgentBus",
        memory: "MemoryStore",
        slow_cycle_threshold_s: float | None = None,
    ) -> None:
        self._bus = bus
        self._memory = memory
        self.slow_cycle_threshold_s = slow_cycle_threshold_s
        self.total_cycles: int = 0
        self.successful_cycles: int = 0
        self.failed_cycles: int = 0
        self.slow_cycles: int = 0
        self.last_duration_s: float = 0.0
        self.cumulative_steps_executed: int = 0
        self.cumulative_steps_skipped: int = 0
        self._current_summary: dict[str, Any] | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def cycle(self) -> "_CycleContext":
        """Return a context manager for one autonomous cycle."""
        return _CycleContext(self)

    def set_summary(self, summary: dict[str, Any]) -> None:
        """Record the cycle's execution summary (called inside the context)."""
        self._current_summary = summary

    def stats(self) -> dict[str, Any]:
        """Return a snapshot of aggregate cycle statistics."""
        success_rate = (
            round(self.successful_cycles / self.total_cycles, 4)
            if self.total_cycles
            else 0.0
        )
        return {
            "total_cycles": self.total_cycles,
            "successful_cycles": self.successful_cycles,
            "failed_cycles": self.failed_cycles,
            "slow_cycles": self.slow_cycles,
            "last_duration_s": self.last_duration_s,
            "cumulative_steps_executed": self.cumulative_steps_executed,
            "cumulative_steps_skipped": self.cumulative_steps_skipped,
            "success_rate": success_rate,
        }

    # ------------------------------------------------------------------
    # Internal helpers (called by _CycleContext)
    # ------------------------------------------------------------------

    def _on_start(self, cycle_index: int) -> None:
        self._current_summary = None
        self._bus.publish(
            self.TOPIC_STARTED,
            {"cycle_index": cycle_index, "timestamp": time.time()},
        )

    def _on_complete(self, cycle_index: int, duration_s: float) -> None:
        summary = self._current_summary or {}
        self.total_cycles += 1
        self.successful_cycles += 1
        self.last_duration_s = duration_s
        self.cumulative_steps_executed += summary.get("executed_steps", 0)
        self.cumulative_steps_skipped += summary.get("skipped_steps", 0)
        event: dict[str, Any] = {
            "cycle_index": cycle_index,
            "duration_s": round(duration_s, 4),
            "executed_steps": summary.get("executed_steps", 0),
            "skipped_steps": summary.get("skipped_steps", 0),
            "failed_steps": summary.get("failed_steps", 0),
            "goal": summary.get("goal", ""),
            "total_cycles": self.total_cycles,
            "successful_cycles": self.successful_cycles,
            "failed_cycles": self.failed_cycles,
        }
        self._bus.publish(self.TOPIC_COMPLETED, event)
        self._memory.write("cycle_metrics", event)

        # Slow-cycle alerting
        threshold = self.slow_cycle_threshold_s
        if threshold is not None and duration_s > threshold:
            self.slow_cycles += 1
            slow_event: dict[str, Any] = {
                "cycle_index": cycle_index,
                "duration_s": round(duration_s, 4),
                "threshold_s": threshold,
                "goal": summary.get("goal", ""),
                "total_cycles": self.total_cycles,
                "slow_cycles": self.slow_cycles,
            }
            self._bus.publish(self.TOPIC_SLOW, slow_event)
            self._memory.write("cycle_slow", slow_event)

    def _on_failure(
        self,
        cycle_index: int,
        duration_s: float,
        exc: BaseException,
    ) -> None:
        self.total_cycles += 1
        self.failed_cycles += 1
        self.last_duration_s = duration_s
        event: dict[str, Any] = {
            "cycle_index": cycle_index,
            "duration_s": round(duration_s, 4),
            "error": str(exc),
            "exception_type": type(exc).__name__,
            "total_cycles": self.total_cycles,
            "successful_cycles": self.successful_cycles,
            "failed_cycles": self.failed_cycles,
        }
        self._bus.publish(self.TOPIC_FAILED, event)
        self._memory.write("cycle_failure", event)


class _CycleContext:
    """Internal context manager yielded by CycleObserver.cycle()."""

    def __init__(self, observer: CycleObserver) -> None:
        self._observer = observer
        self._cycle_index = observer.total_cycles
        self._start: float = 0.0

    def set_summary(self, summary: dict[str, Any]) -> None:
        self._observer.set_summary(summary)

    def __enter__(self) -> "_CycleContext":
        self._start = time.monotonic()
        self._observer._on_start(self._cycle_index)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> bool:
        duration = time.monotonic() - self._start
        if exc_val is not None:
            self._observer._on_failure(self._cycle_index, duration, exc_val)
            return False  # re-raise
        self._observer._on_complete(self._cycle_index, duration)
        return False
