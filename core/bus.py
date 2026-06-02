"""Thread-safe pub/sub bus for lightweight agent coordination."""
from __future__ import annotations

from collections import defaultdict
import threading
from typing import Any, Callable, DefaultDict, Dict, List


class AgentBus:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._subscribers: DefaultDict[
            str,
            List[Callable[[Dict[str, Any]], Any]],
        ] = defaultdict(list)

    def subscribe(
        self,
        topic: str,
        callback: Callable[[Dict[str, Any]], Any],
    ) -> None:
        with self._lock:
            self._subscribers[topic].append(callback)

    def unsubscribe(
        self,
        topic: str,
        callback: Callable[[Dict[str, Any]], Any],
    ) -> None:
        with self._lock:
            callbacks = self._subscribers.get(topic, [])
            self._subscribers[topic] = [
                entry for entry in callbacks if entry is not callback
            ]
            if not self._subscribers[topic]:
                self._subscribers.pop(topic, None)

    def publish(self, topic: str, message: Dict[str, Any]) -> List[Any]:
        """Deliver ``message`` to every subscriber of ``topic``.

        Reliability contract:
        - Each subscriber is invoked with its own shallow copy of ``message``
          so one subscriber cannot mutate the payload seen by the next.
        - A subscriber that raises does not abort delivery to the remaining
          subscribers; its failure is captured as a structured error result
          (``{"error", "exception_type", "exception"}``) instead of being
          propagated to the caller.
        - The returned list preserves subscriber order, so each entry
          corresponds positionally to the subscriber that produced it.
        """
        with self._lock:
            callbacks = list(self._subscribers.get(topic, []))
        results: List[Any] = []
        for callback in callbacks:
            try:
                results.append(callback(dict(message)))
            except Exception as exc:
                results.append(
                    {
                        "error": "Subscriber callback failed",
                        "exception_type": type(exc).__name__,
                        "exception": str(exc),
                    }
                )
        return results
