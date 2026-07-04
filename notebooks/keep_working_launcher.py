#!/usr/bin/env python3
"""CLI launcher for Keep Working Pomodoro tool.

Usage: python notebooks/keep_working_launcher.py --task "Write code" --work 1500
"""

import argparse
import datetime
import getpass
import json
import platform
import shlex
import shutil
import sqlite3
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class SessionRecord:
    task_name: str
    start_ts: str
    end_ts: str
    duration_s: int
    kind: str


HISTORY_JSON = Path("notebooks") / "keep_working_history.json"
HISTORY_DB = Path("notebooks") / "keep_working_history.db"
CONFIG_PATH = Path("notebooks") / "keep_working_config.json"


# Default notebook/CLI UI settings. Persisted to CONFIG_PATH so the notebook UI
# remembers the user's last task name, durations, and toggles across restarts.
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


def load_config(path=CONFIG_PATH):
    """Load persisted UI settings, merged over defaults.

    Unknown keys are ignored and missing keys fall back to ``DEFAULT_SETTINGS``.
    A missing or corrupt config file yields a copy of the defaults.
    """
    path = Path(path)
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError, ValueError):
            data = None
        if isinstance(data, dict):
            return {key: data.get(key, default) for key, default in DEFAULT_SETTINGS.items()}
    return dict(DEFAULT_SETTINGS)


def save_config(settings, path=CONFIG_PATH):
    """Persist UI settings to ``path`` as JSON, keeping only known keys.

    Returns the cleaned settings dict that was written.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    settings = settings or {}
    cleaned = {key: settings.get(key, default) for key, default in DEFAULT_SETTINGS.items()}
    path.write_text(json.dumps(cleaned, indent=2))
    return cleaned


def append_json_record(rec: SessionRecord, path=HISTORY_JSON):
    path.parent.mkdir(parents=True, exist_ok=True)
    arr = []
    if path.exists():
        arr = json.loads(path.read_text())
    arr.append(asdict(rec))
    path.write_text(json.dumps(arr, indent=2))


def init_db(path=HISTORY_DB):
    conn = sqlite3.connect(str(path))
    cur = conn.cursor()
    cur.execute(
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
    conn.commit()
    conn.close()


def append_db_record(rec: SessionRecord, path=HISTORY_DB):
    init_db(path)
    conn = sqlite3.connect(str(path))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions(task_name, start_ts, end_ts, duration_s, kind) VALUES (?,?,?,?,?)",
        (rec.task_name, rec.start_ts, rec.end_ts, rec.duration_s, rec.kind),
    )
    conn.commit()
    conn.close()


def send_notification(title: str, message: str):
    """Try plyer, then platform-specific fallbacks, else print."""
    try:
        from plyer import notification as plyer_notification

        plyer_notification.notify(title=title, message=message)
        return
    except Exception:
        pass
    system = platform.system()
    try:
        if system == "Linux" and shutil.which("notify-send"):
            subprocess.run(["notify-send", title, message])
            return
        if system == "Darwin":
            # macOS: use osascript
            subprocess.run(["osascript", "-e", f'display notification "{message}" with title "{title}"'])
            return
    except Exception:
        pass
    # fallback
    print(f"NOTIFY: {title} - {message}")


def play_sound():
    """Play a short beep where possible; fallback to terminal bell."""
    try:
        if platform.system() == "Windows":
            import winsound

            winsound.MessageBeep(winsound.MB_OK)
            return
    except Exception:
        pass
    # Best-effort: system bell
    try:
        print("\a", end="", flush=True)
    except Exception:
        pass


def update_status_file(path, rec=None, cycle_count=None, running=False):
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if p.exists():
        try:
            data = json.loads(p.read_text())
        except Exception:
            data = {}
    data.update(
        {
            "last_session": asdict(rec) if rec else None,
            "cycle_count": cycle_count,
            "running": running,
            "updated_at": datetime.datetime.utcnow().isoformat(),
        }
    )
    p.write_text(json.dumps(data, indent=2))


def export_systemd(
    path,
    python_exec=None,
    workspace_dir=None,
    task="Keep Working",
    work=1500,
    short=300,
    long=900,
    cycles_per_long=4,
    notify=False,
    sound=False,
    repeat=False,
):
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    if python_exec is None:
        python_exec = sys.executable or "python3"
    if workspace_dir is None:
        workspace_dir = str(Path.cwd())
    launcher = str(Path(workspace_dir) / "notebooks" / "keep_working_launcher.py")
    args = [
        python_exec,
        launcher,
        "--task",
        task,
        "--work",
        str(work),
        "--short",
        str(short),
        "--long",
        str(long),
        "--cycles-per-long",
        str(cycles_per_long),
    ]
    if notify:
        args.append("--notify")
    if sound:
        args.append("--sound")
    if repeat:
        args.append("--repeat")
    exec_cmd = " ".join(shlex.quote(a) for a in args)
    content = f"""[Unit]
Description=Keep Working Pomodoro Service

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
    p.write_text(content)
    return str(p)


def run_session(seconds, task_name, kind="work", notify=False, sound=False):
    """Run a blocking session (work or break) and persist the record.

    Returns SessionRecord on success, None on KeyboardInterrupt.
    """
    start = datetime.datetime.utcnow()
    label = task_name if kind == "work" else f"{kind.replace('_', ' ').title()}"
    print(f"Starting {label}: {task_name} for {seconds} seconds")
    try:
        for remaining in range(seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            print(f"\rRemaining: {mins:02d}:{secs:02d}", end="", flush=True)
            time.sleep(1)
        print(f"\n{label} finished")
    except KeyboardInterrupt:
        print("\nInterrupted")
        return None
    end = datetime.datetime.utcnow()
    rec = SessionRecord(
        task_name=task_name, start_ts=start.isoformat(), end_ts=end.isoformat(), duration_s=seconds, kind=kind
    )
    append_json_record(rec)
    append_db_record(rec)
    print("Logged session:", rec)
    # notifications
    if notify:
        send_notification("Keep Working", f"{kind} finished: {task_name}")
    if sound:
        play_sound()
    return rec


def main():
    # Load persisted notebook UI settings; CLI flags override these.
    cfg = load_config()

    p = argparse.ArgumentParser(
        description="Keep Working Pomodoro launcher. Reads defaults from notebooks/keep_working_config.json; explicit flags override.",
    )
    p.add_argument("--task", help="Task name")
    p.add_argument("--work", type=int, help="Work duration in seconds")
    p.add_argument("--short", type=int, help="Short break seconds")
    p.add_argument("--long", type=int, help="Long break seconds")
    p.add_argument(
        "--cycles-per-long", type=int, dest="cycles_per_long", help="Number of work cycles before a long break"
    )
    p.add_argument("--cycles", type=int, default=1, help="Number of work cycles to run (ignored with --repeat)")
    p.add_argument("--repeat", action="store_true", default=None, help="Repeat cycles indefinitely until interrupted")
    p.add_argument("--no-breaks", action="store_true", help="Do not run breaks between work sessions")
    p.add_argument(
        "--notify", action="store_true", default=None, help="Show desktop notification when a session finishes"
    )
    p.add_argument(
        "--sound", action="store_true", default=None, help="Play a short sound (bell) when a session finishes"
    )
    p.add_argument(
        "--status-file",
        type=str,
        dest="status_file",
        default=None,
        help="Write a JSON status file with last_session and running state",
    )
    p.add_argument(
        "--export-systemd", type=str, default=None, help="Export a systemd user service file to the given path and exit"
    )
    p.add_argument(
        "--install-systemd",
        action="store_true",
        help="Write service to ~/.config/systemd/user/keep-working.service and print enable instructions",
    )
    p.add_argument(
        "--no-config", action="store_true", help="Ignore notebooks/keep_working_config.json and use built-in defaults"
    )

    # Apply config values as argparse defaults so explicit CLI flags still win.
    if not any(a == "--no-config" for a in sys.argv[1:]):
        p.set_defaults(
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
    else:
        p.set_defaults(
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

    args = p.parse_args()

    # If exporting systemd service, write file and exit
    if args.export_systemd:
        svc_path = export_systemd(
            args.export_systemd,
            python_exec=sys.executable,
            workspace_dir=str(Path.cwd()),
            task=args.task,
            work=args.work,
            short=args.short,
            long=args.long,
            cycles_per_long=args.cycles_per_long,
            notify=args.notify,
            sound=args.sound,
            repeat=args.repeat,
        )
        print("Wrote systemd service to", svc_path)
        print(
            "To enable: copy to ~/.config/systemd/user/ and run `systemctl --user daemon-reload && systemctl --user enable --now <name>`"
        )
        return
    if args.install_systemd:
        user_path = Path("~/.config/systemd/user/keep-working.service").expanduser()
        svc_path = export_systemd(
            str(user_path),
            python_exec=sys.executable,
            workspace_dir=str(Path.cwd()),
            task=args.task,
            work=args.work,
            short=args.short,
            long=args.long,
            cycles_per_long=args.cycles_per_long,
            notify=args.notify,
            sound=args.sound,
            repeat=args.repeat,
        )
        print("Installed systemd service to", svc_path)
        print("Run: systemctl --user daemon-reload && systemctl --user enable --now keep-working.service")
        return

    cycle_count = 0
    try:
        while True:
            cycle_count += 1
            # Run work session
            # update status before starting
            if args.status_file:
                update_status_file(args.status_file, rec=None, cycle_count=cycle_count, running=True)
            rec = run_session(args.work, args.task, kind="work", notify=args.notify, sound=args.sound)
            if rec is None:
                break  # interrupted

            # write status after session
            if args.status_file:
                update_status_file(args.status_file, rec=rec, cycle_count=cycle_count, running=False)

            # Determine whether to stop
            if not args.repeat and args.cycles and cycle_count >= args.cycles:
                print("Completed requested cycles; exiting")
                break

            if args.no_breaks:
                continue

            # Choose break type
            if args.cycles_per_long > 0 and (cycle_count % args.cycles_per_long) == 0:
                # long break
                bkind = "long_break"
                bsecs = args.long
            else:
                bkind = "short_break"
                bsecs = args.short

            brec = run_session(bsecs, f"Break after {args.task}", kind=bkind, notify=args.notify, sound=args.sound)
            if brec is None:
                break

            # loop continues (repeat or until cycles exhausted)
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt; exiting")


if __name__ == "__main__":
    main()
