"""
Aria Async Task Queue
"""

from __future__ import annotations

import asyncio
from contextlib import suppress


_STOP = object()

class TaskQueue:
    def __init__(self, max_workers=5):
        self.queue = asyncio.Queue()
        self.max_workers = max_workers
        self.workers = []
        self.running = False

    async def add_task(self, task):
        await self.queue.put(task)

    async def worker(self, handler):
        while True:
            task = await self.queue.get()
            try:
                if task is _STOP:
                    return
                await handler(task)
            except Exception as e:
                print("[Queue error]", e)
            finally:
                self.queue.task_done()

    async def start(self, handler):
        if self.running:
            return
        self.running = True
        for _ in range(self.max_workers):
            self.workers.append(asyncio.create_task(self.worker(handler)))

    async def stop(self):
        if not self.running:
            return
        self.running = False
        for _ in self.workers:
            await self.queue.put(_STOP)
        await self.queue.join()
        for w in self.workers:
            w.cancel()
            with suppress(asyncio.CancelledError):
                await w
        self.workers.clear()

    def pending_count(self) -> int:
        return self.queue.qsize()
