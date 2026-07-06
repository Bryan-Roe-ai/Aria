"""WebSocket server for real-time job updates"""

import asyncio
import json
import os
from contextlib import suppress
from datetime import datetime
from importlib import import_module
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

websockets = import_module("websockets")
ConnectionClosed = websockets.exceptions.ConnectionClosed

# Track connected clients
clients = set()

# Job status cache
job_status_cache = {}


class JobFileHandler(FileSystemEventHandler):
    """Monitor job status files for changes"""

    def __init__(self, loop, broadcast_func):
        self.loop = loop
        self.broadcast = broadcast_func

    def on_modified(self, event):
        src_path = os.fsdecode(event.src_path)

        if src_path.endswith(".json") and "status" in src_path:
            asyncio.run_coroutine_threadsafe(
                self.broadcast_status_update(src_path),
                self.loop,
            )

    async def broadcast_status_update(self, file_path):
        """Broadcast status update to all connected clients"""
        try:
            with open(file_path, encoding="utf-8") as file_obj:
                status = json.load(file_obj)
        except (OSError, json.JSONDecodeError) as error:
            print(f"Error broadcasting update: {error}")
            return

        message = {
            "type": "job_update",
            "timestamp": datetime.now().isoformat(),
            "data": status,
        }

        await self.broadcast(message)


async def broadcast_message(message):
    """Send message to all connected clients"""
    if clients:
        message_str = json.dumps(message)
        await asyncio.gather(
            *[
                client.send(message_str)
                for client in tuple(clients)
            ],
            return_exceptions=True,
        )


async def websocket_handler(websocket, _path):
    """Handle WebSocket connections"""
    del _path

    # Register client
    clients.add(websocket)
    print(f"Client connected. Total clients: {len(clients)}")

    try:
        # Send initial status
        initial_status = get_current_status()
        await websocket.send(
            json.dumps(
                {
                    "type": "initial_status",
                    "timestamp": datetime.now().isoformat(),
                    "data": initial_status,
                }
            )
        )

        # Keep connection alive and handle messages
        async for message in websocket:
            try:
                data = json.loads(message)

                if data.get("type") == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))

                elif data.get("type") == "request_status":
                    status = get_current_status()
                    await websocket.send(
                        json.dumps(
                            {
                                "type": "status_response",
                                "timestamp": datetime.now().isoformat(),
                                "data": status,
                            }
                        )
                    )

            except json.JSONDecodeError:
                await websocket.send(
                    json.dumps(
                        {
                            "type": "error",
                            "message": "Invalid JSON",
                        }
                    )
                )

    except ConnectionClosed as error:
        print(
            "Client connection closed: "
            f"code={error.code}, reason={error.reason}"
        )
    finally:
        # Unregister client
        clients.discard(websocket)
        print(f"Client disconnected. Total clients: {len(clients)}")


def get_current_status():
    """Get current training job status"""
    status_dir = Path("data_out/autotrain")
    jobs = []

    if status_dir.exists():
        for status_file in status_dir.glob("**/status.json"):
            try:
                with open(status_file, encoding="utf-8") as file_obj:
                    job_data = json.load(file_obj)
                jobs.append(job_data)
            except (OSError, json.JSONDecodeError) as error:
                print(f"Error reading {status_file}: {error}")

    return {
        "jobs": jobs,
        "timestamp": datetime.now().isoformat(),
        "active_count": len(
            [
                job
                for job in jobs
                if job.get("status") == "running"
            ]
        ),
    }


async def periodic_heartbeat():
    """Send periodic heartbeat to keep connections alive"""
    while True:
        await asyncio.sleep(30)

        if clients:
            status = get_current_status()
            message = {
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat(),
                "data": status,
            }
            await broadcast_message(message)


async def main():
    """Start WebSocket server and file watcher"""
    print("Starting WebSocket server on ws://localhost:8765")

    # Setup file system watcher
    observer = Observer()
    loop = asyncio.get_running_loop()
    file_handler = JobFileHandler(loop, broadcast_message)

    watch_dir = Path("data_out")
    if watch_dir.exists():
        observer.schedule(
            file_handler,
            str(watch_dir),
            recursive=True,
        )
        observer.start()
        print(f"Watching {watch_dir} for changes...")

    try:
        async with websockets.serve(
            websocket_handler,
            "localhost",
            8765,
        ):
            heartbeat_task = asyncio.create_task(
                periodic_heartbeat()
            )

            print("WebSocket server ready!")
            print("Connect clients to: ws://localhost:8765")

            try:
                await asyncio.Future()
            finally:
                heartbeat_task.cancel()
                with suppress(asyncio.CancelledError):
                    await heartbeat_task
    finally:
        if observer.is_alive():
            observer.stop()
            observer.join()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down WebSocket server...")
