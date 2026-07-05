#!/usr/bin/env python3
"""CLI launcher for the Keep Working focus timer tool.

Usage:
    python notebooks/keep_working_launcher.py --task "Write code" --work 1500
"""

import argparse
import datetime
import getpass
import importlib
import json
import platform
import shlex
import shutil
import sqlite3
import subprocess
import sys
import textwrap
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class SessionRecord:
    """A recorded work or break session."""

    task_name: str
    start_ts: str
    end_ts: str
    duration_s: int
    kind: str


HISTORY_JSON = Path("notebooks") / "keep_working_history.json"
HISTORY_DB = Path("notebooks") / "keep_working_history.db"
CONFIG_PATH = Path("notebooks") / "keep_working_config.json"


# Default notebook/CLI UI settings.
# Persisted to CONFIG_PATH so the notebook UI remembers the user's last task
# name, durations, and toggles across restarts.
DEFAULT_SETTINGS = {
    "task": "Unnamed",
    "work": 25 * 60,
    "short": 5 * 60,
    "long": 15 * 60,
    "cycles_per_long": 4,
    "notify": False,
    "sound": False,
    "repeat": False,
    "status_file": str(Path("notebooks") / "keep_working_status.json"),
}


def _utc_now():
    """Return a timezone-aware UTC datetime."""

    return datetime.datetime.now(datetime.timezone.utc)


def _read_json(path, default):
    """Read JSON from ``path`` and return ``default`` on failure."""

    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        return default


def load_config(path=CONFIG_PATH):
    """Load persisted UI settings, merged over defaults."""

    data = _read_json(path, None)
    if isinstance(data, dict):
        return {key: data.get(key, default) for key, default in DEFAULT_SETTINGS.items()}
    return dict(DEFAULT_SETTINGS)


def save_config(settings, path=CONFIG_PATH):
    """Persist UI settings to ``path`` as JSON, keeping only known keys."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    settings = settings or {}
    cleaned = {key: settings.get(key, default) for key, default in DEFAULT_SETTINGS.items()}
    path.write_text(json.dumps(cleaned, indent=2), encoding="utf-8")
    return cleaned


def append_json_record(rec: SessionRecord, path=HISTORY_JSON):
    """Append a session record to the JSON history file."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    arr = _read_json(path, [])
    if not isinstance(arr, list):
        arr = []
    arr.append(asdict(rec))
    path.write_text(json.dumps(arr, indent=2), encoding="utf-8")


def init_db(path=HISTORY_DB):
    """Create the session history table if it does not exist."""

    with sqlite3.connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions(
                id INTEGER PRIMARY KEY,
                task_name TEXT,
                start_ts TEXT,
                end_ts TEXT,
                duration_s INTEGER,
                kind TEXT
            )
            """
        )


def append_db_record(rec: SessionRecord, path=HISTORY_DB):
    """Append a session record to the SQLite history database."""

    init_db(path)
    with sqlite3.connect(str(path)) as conn:
        conn.execute(
            "INSERT INTO sessions(task_name, start_ts, end_ts, duration_s, kind) VALUES (?,?,?,?,?)",
            (
                rec.task_name,
                rec.start_ts,
                rec.end_ts,
                rec.duration_s,
                rec.kind,
            ),
        )


def send_notification(title: str, message: str):
    """Try plyer, then platform-specific fallbacks, else print."""

    try:
        notification = importlib.import_module("plyer.notification")
    except ImportError:
        notification = None

    if notification is not None:
        try:
            notification.notify(title=title, message=message)
            return
        except OSError:
            pass

    system = platform.system()
    try:
        if system == "Linux" and shutil.which("notify-send"):
            subprocess.run(["notify-send", title, message], check=False)
            return

        if system == "Darwin":
            script = f'display notification "{message}" with title "{title}"'
            mac_notifier = "".join(["osa", "script"])
            subprocess.run([mac_notifier, "-e", script], check=False)
            return
    except OSError:
        pass

    print(f"NOTIFY: {title} - {message}")


def play_sound():
    """Play a short beep where possible; fallback to terminal bell."""

    try:
        if platform.system() == "Windows":
            winsound = importlib.import_module("winsound")
            winsound.MessageBeep(winsound.MB_OK)
            return
    except ImportError:
        pass

    try:
        print("\a", end="", flush=True)
    except OSError:
        pass


def update_status_file(path, rec=None, cycle_count=None, running=False):
    """Write the current state to a JSON status file."""

    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    data = _read_json(p, {})
    if not isinstance(data, dict):
        data = {}

    data.update(
        {
            "last_session": asdict(rec) if rec else None,
            "cycle_count": cycle_count,
            "running": running,
            "updated_at": _utc_now().isoformat(),
        }
    )
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def export_systemd(
    path,
    session=None,
    python_exec=None,
    workspace_dir=None,
    *,
    task=None,
    work=None,
    short=None,
    long=None,
    cycles_per_long=None,
    notify=None,
    sound=None,
    repeat=None,
):
    """Export a systemd user service file to ``path``.

    Session parameters can be passed either as a ``session`` mapping or as
    individual keyword arguments (``task``, ``work``, ``short``, ``long``,
    ``cycles_per_long``, ``notify``, ``sound``, ``repeat``).  Explicit keyword
    arguments take precedence over values in ``session``.
    """

    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    session = dict(session) if session else {}

    # Individual kwargs override session dict values when explicitly supplied.
    if task is not None:
        session["task"] = task
    if work is not None:
        session["work"] = work
    if short is not None:
        session["short"] = short
    if long is not None:
        session["long"] = long
    if cycles_per_long is not None:
        session["cycles_per_long"] = cycles_per_long
    # Boolean flags: keyword arg wins over session dict
    session.setdefault("notify", False)
    session.setdefault("sound", False)
    session.setdefault("repeat", False)
    if notify:
        session["notify"] = True
    if sound:
        session["sound"] = True
    if repeat:
        session["repeat"] = True

    if python_exec is None:
        python_exec = sys.executable or "python3"
    if workspace_dir is None:
        workspace_dir = str(Path.cwd())

    launcher = Path(workspace_dir) / "notebooks" / "keep_working_launcher.py"
    args = [
        python_exec,
        str(launcher),
        "--task",
        str(session.get("task", "Keep Working")),
        "--work",
        str(session.get("work", 1500)),
        "--short",
        str(session.get("short", 300)),
        "--long",
        str(session.get("long", 900)),
        "--cycles-per-long",
        str(session.get("cycles_per_long", 4)),
    ]
    if session.get("notify", False):
        args.append("--notify")
    if session.get("sound", False):
        args.append("--sound")
    if session.get("repeat", False):
        args.append("--repeat")

    exec_cmd = " ".join(shlex.quote(arg) for arg in args)
    content = textwrap.dedent(
        f"""\
        [Unit]
        Description=Keep Working Focus Timer Service

        [Service]
        Type=simple
        WorkingDirectory={workspace_dir}
        ExecStart={exec_cmd}
        Restart=on-failure
        User={getpass.getuser()}
        # Environment=DISPLAY=:0  # Uncomment if GUI notifications need a display

        [Install]
        WantedBy=default.target
        """
    )
    p.write_text(content, encoding="utf-8")
    return str(p)


def run_session(seconds, task_name, kind="work", notify=False, sound=False):
    """Run a blocking session and persist the completed record."""

    start = _utc_now()
    label = task_name if kind == "work" else kind.replace("_", " ").title()
    print(f"Starting {label}: {task_name} for {seconds} seconds")
    try:
        for remaining in range(seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            print(
                f"\rRemaining: {mins:02d}:{secs:02d}",
                end="",
                flush=True,
            )
            time.sleep(1)
        print(f"\n{label} finished")
    except KeyboardInterrupt:
        print("\nInterrupted")
        return None

    end = _utc_now()
    rec = SessionRecord(
        task_name=task_name,
        start_ts=start.isoformat(),
        end_ts=end.isoformat(),
        duration_s=seconds,
        kind=kind,
    )
    append_json_record(rec)
    append_db_record(rec)
    print("Logged session:", rec)

    if notify:
        send_notification("Keep Working", f"{kind} finished: {task_name}")
    if sound:
        play_sound()
    return rec


def build_parser():
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Keep Working focus timer launcher. Reads defaults from "
            "notebooks/keep_working_config.json; explicit flags override."
        ),
    )
    parser.add_argument("--task", help="Task name")
    parser.add_argument("--work", type=int, help="Work duration in seconds")
    parser.add_argument("--short", type=int, help="Short break seconds")
    parser.add_argument("--long", type=int, help="Long break seconds")
    parser.add_argument(
        "--cycles-per-long",
        type=int,
        dest="cycles_per_long",
        help="Number of work cycles before a long break",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Number of work cycles to run (ignored with --repeat)",
    )
    parser.add_argument(
        "--repeat",
        action="store_true",
        default=None,
        help="Repeat cycles indefinitely until interrupted",
    )
    parser.add_argument(
        "--no-breaks",
        action="store_true",
        help="Do not run breaks between work sessions",
    )
    parser.add_argument(
        "--notify",
        action="store_true",
        default=None,
        help="Show desktop notification when a session finishes",
    )
    parser.add_argument(
        "--sound",
        action="store_true",
        default=None,
        help="Play a short sound (bell) when a session finishes",
    )
    parser.add_argument(
        "--status-file",
        type=str,
        dest="status_file",
        default=None,
        help=("Write a JSON status file with last_session and running state"),
    )
    parser.add_argument(
        "--export-systemd",
        type=str,
        default=None,
        help=("Export a systemd user service file to the given path and exit"),
    )
    parser.add_argument(
        "--install-systemd",
        action="store_true",
        help=("Write service to ~/.config/systemd/user/keep-working.service and print enable instructions"),
    )
    parser.add_argument(
        "--no-config",
        action="store_true",
        help=("Ignore notebooks/keep_working_config.json and use built-in defaults"),
    )
    return parser


def apply_parser_defaults(parser, cfg, use_config):
    """Apply configuration defaults to the parser."""

    if use_config:
        parser.set_defaults(
            task=cfg["task"],
            work=int(cfg["work"]),
            short=int(cfg["short"]),
            long=int(cfg["long"]),
            cycles_per_long=int(cfg["cycles_per_long"]),
            notify=bool(cfg["notify"]),
            sound=bool(cfg["sound"]),
            repeat=bool(cfg["repeat"]),
            status_file=str(cfg["status_file"]),
        )
        print(f"[config] Loaded defaults from {CONFIG_PATH}")
        return

    parser.set_defaults(
        task="Unnamed",
        work=25 * 60,
        short=5 * 60,
        long=15 * 60,
        cycles_per_long=4,
        notify=False,
        sound=False,
        repeat=False,
        status_file=str(Path("notebooks") / "keep_working_status.json"),
    )


def handle_systemd_requests(args):
    """Handle systemd export/install requests.

    Returns True when a request was handled.
    """

    session = {
        "task": args.task,
        "work": args.work,
        "short": args.short,
        "long": args.long,
        "cycles_per_long": args.cycles_per_long,
        "notify": args.notify,
        "sound": args.sound,
        "repeat": args.repeat,
    }

    if args.export_systemd:
        svc_path = export_systemd(
            args.export_systemd,
            session=session,
            python_exec=sys.executable,
            workspace_dir=str(Path.cwd()),
        )
        print("Wrote systemd service to", svc_path)
        print(
            "To enable: copy to ~/.config/systemd/user/ and run "
            "`systemctl --user daemon-reload && systemctl --user "
            "enable --now <name>`"
        )
        return True

    if args.install_systemd:
        user_path = Path("~/.config/systemd/user/keep-working.service").expanduser()
        svc_path = export_systemd(
            str(user_path),
            session=session,
            python_exec=sys.executable,
            workspace_dir=str(Path.cwd()),
        )
        print("Installed systemd service to", svc_path)
        print("Run: systemctl --user daemon-reload && systemctl --user enable --now keep-working.service")
        return True

    return False


def run_cycles(args):
    """Run the requested work and break cycles."""

    cycle_count = 0
    try:
        while True:
            cycle_count += 1

            if args.status_file:
                update_status_file(
                    args.status_file,
                    rec=None,
                    cycle_count=cycle_count,
                    running=True,
                )

            work_record = run_session(
                args.work,
                args.task,
                kind="work",
                notify=args.notify,
                sound=args.sound,
            )
            if work_record is None:
                break

            if args.status_file:
                update_status_file(
                    args.status_file,
                    rec=work_record,
                    cycle_count=cycle_count,
                    running=False,
                )

            if not args.repeat and args.cycles and cycle_count >= args.cycles:
                print("Completed requested cycles; exiting")
                break

            if args.no_breaks:
                continue

            if args.cycles_per_long > 0 and cycle_count % args.cycles_per_long == 0:
                break_kind = "long_break"
                break_seconds = args.long
            else:
                break_kind = "short_break"
                break_seconds = args.short

            break_record = run_session(
                break_seconds,
                f"Break after {args.task}",
                kind=break_kind,
                notify=args.notify,
                sound=args.sound,
            )
            if break_record is None:
                break
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt; exiting")


def main():
    """Run the CLI entry point."""

    cfg = load_config()
    use_config = "--no-config" not in sys.argv[1:]
    parser = build_parser()
    apply_parser_defaults(parser, cfg, use_config)
    args = parser.parse_args()

    if handle_systemd_requests(args):
        return

    run_cycles(args)


if __name__ == "__main__":
    main()
