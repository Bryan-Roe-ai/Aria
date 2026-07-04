import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest


def _port_is_bindable(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
        except OSError:
            return False
        return True


def test_server_startable_with_sys_executable():
    """Regression test: starting aria_web/server.py using sys.executable
    should open port 8080."""
    ARIA_WEB = Path(__file__).resolve().parents[1] / "aria_web"

    if not _port_is_bindable("127.0.0.1", 8080):
        pytest.skip("port 8080 is already in use in this environment")

    proc = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=str(ARIA_WEB),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        # wait up to 5s for server to accept connections
        for _ in range(50):
            try:
                s = socket.create_connection(("127.0.0.1", 8080), timeout=0.5)
                s.close()
                break
            except OSError:
                time.sleep(0.1)
        else:
            pytest.fail("aria_web/server.py did not open port 8080 when started with sys.executable")
    finally:
        proc.kill()
        proc.wait(timeout=2)
