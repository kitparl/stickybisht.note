"""Unix-socket IPC for single-instance StickyBisht control."""

from __future__ import annotations

import socket
import threading
from pathlib import Path
from queue import Empty, Queue
from typing import Callable, Optional

SOCKET_DIR = Path.home() / ".stickybisht"
SOCKET_PATH = SOCKET_DIR / "ctl.sock"

VALID_COMMANDS = frozenset({"show", "hide", "toggle", "quit", "ping"})


def ensure_socket_dir() -> None:
    SOCKET_DIR.mkdir(parents=True, exist_ok=True)


def send_command(command: str, timeout: float = 1.0) -> Optional[str]:
    """
    Send a command to a running instance.

    Returns the response string, or None if no server is reachable.
    """
    if command not in VALID_COMMANDS:
        raise ValueError(f"Unknown command: {command}")

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect(str(SOCKET_PATH))
            sock.sendall((command + "\n").encode("utf-8"))
            data = sock.recv(256)
            return data.decode("utf-8").strip() if data else "ok"
    except (FileNotFoundError, ConnectionRefusedError, OSError):
        return None


def is_server_running() -> bool:
    """Return True if a live instance responds to ping."""
    return send_command("ping") is not None


class ControlServer:
    """
    Listen on a Unix socket and push commands into a queue for the Tk thread.

    Call start() after creating the Tk root. Drain the queue from the main
    thread via root.after — never call Tk APIs from the listener thread.
    """

    def __init__(self) -> None:
        self.queue: Queue[str] = Queue()
        self._sock: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()

    def start(self) -> bool:
        """
        Bind the control socket and start the listener thread.

        Returns False if another live instance already owns the socket.
        """
        ensure_socket_dir()

        if is_server_running():
            return False

        if SOCKET_PATH.exists():
            # Stale socket from a crashed previous run.
            try:
                SOCKET_PATH.unlink()
            except OSError:
                pass

        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.bind(str(SOCKET_PATH))
        self._sock.listen(5)
        self._sock.settimeout(0.5)

        self._stop.clear()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        return True

    def _listen_loop(self) -> None:
        assert self._sock is not None
        while not self._stop.is_set():
            try:
                conn, _ = self._sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            with conn:
                try:
                    raw = conn.recv(256).decode("utf-8").strip()
                except OSError:
                    continue

                if not raw:
                    continue

                command = raw.split()[0].lower()
                if command not in VALID_COMMANDS:
                    try:
                        conn.sendall(b"error: unknown\n")
                    except OSError:
                        pass
                    continue

                if command == "ping":
                    try:
                        conn.sendall(b"pong\n")
                    except OSError:
                        pass
                    continue

                self.queue.put(command)
                try:
                    conn.sendall(b"ok\n")
                except OSError:
                    pass

    def drain(self, handler: Callable[[str], None]) -> None:
        """Process all pending commands on the Tk thread."""
        while True:
            try:
                command = self.queue.get_nowait()
            except Empty:
                break
            handler(command)

    def stop(self) -> None:
        self._stop.set()
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        if SOCKET_PATH.exists():
            try:
                SOCKET_PATH.unlink()
            except OSError:
                pass
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
