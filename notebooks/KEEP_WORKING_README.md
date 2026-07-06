# Keep Working — Pomodoro Productivity Tool

A lightweight Pomodoro timer with CLI launcher, Jupyter notebook UI, desktop notifications, and session history.

## Quick Start (CLI)

```bash
# Single 25-minute work session (defaults)
python notebooks/keep_working_launcher.py --task "Write docs"

# Short demo: 2 cycles, 3-second work, 2-second breaks
python notebooks/keep_working_launcher.py --task Demo --work 3 --short 2 --cycles 2

# Infinite repeat with notifications and sound
python notebooks/keep_working_launcher.py --task "Deep work" --repeat --notify --sound
```

## CLI Flags

| Flag                | Default         | Description                         |
| ------------------- | --------------- | ----------------------------------- |
| `--task`            | `Unnamed`       | Task name logged in history         |
| `--work`            | `1500` (25 min) | Work session duration in seconds    |
| `--short`           | `300` (5 min)   | Short break duration in seconds     |
| `--long`            | `900` (15 min)  | Long break duration in seconds      |
| `--cycles-per-long` | `4`             | Work cycles before a long break     |
| `--cycles`          | `1`             | Total work cycles to run            |
| `--repeat`          | off             | Loop forever (Ctrl+C to stop)       |
| `--no-breaks`       | off             | Skip breaks between work sessions   |
| `--notify`          | off             | Desktop notification on session end |
| `--sound`           | off             | Terminal bell on session end        |

## Notebook UI

Open `notebooks/keep_working.ipynb` in VS Code or JupyterLab. Run all cells to get:

- **Timer controls** — Start / Stop / Reset / Skip buttons with live countdown
- **Cycle settings** — Work, break, and cycles-per-long-break inputs
- **Run/Stop toggle** — Starts a full Pomodoro loop with automatic breaks
- **Visualization** — Bar chart of daily session counts
- **Export** — CSV export of session history

## Notifications

The `--notify` flag tries these in order:

1. **plyer** (`pip install plyer`) — cross-platform desktop notifications
2. **notify-send** (Linux) / **osascript** (macOS) — native fallback
3. **print** — last resort console message

The `--sound` flag plays a terminal bell (`\a`), or `winsound` on Windows.

## Session History

Every completed session is saved to both:

- `notebooks/keep_working_history.json` — human-readable JSON array
- `notebooks/keep_working_history.db` — SQLite database

## Running as a Service (Linux systemd)

A template is provided at `notebooks/keep_working_systemd.service.template`.

```bash
# Copy and edit the template
cp notebooks/keep_working_systemd.service.template ~/.config/systemd/user/keep-working.service
# Edit ExecStart path, user, and WorkingDirectory as needed

# Enable and start
systemctl --user daemon-reload
systemctl --user enable --now keep-working.service

# Check status / logs
systemctl --user status keep-working.service
journalctl --user -u keep-working.service -f
```

## VS Code Task

A **"Keep Working: Pomodoro"** task is available in the VS Code task runner
(`Ctrl+Shift+P` → `Tasks: Run Task`). It launches the CLI in repeat mode with
notifications and sound enabled.

## Status File

Use `--status-file /path/to/status.json` to have the launcher write a small
JSON file after each session with the last session and running state. This is
useful for shell scripts or external monitors that need a simple, machine-
readable status check.

## Exporting systemd

You can export a ready-to-edit systemd unit from the CLI with:

```bash
python notebooks/keep_working_launcher.py --export-systemd /tmp/keep_working.service --task "Focus" --work 1500 --repeat --notify --sound
```

Or install to your user units directory:

```bash
python notebooks/keep_working_launcher.py --install-systemd --task "Focus" --work 1500 --repeat --notify --sound
```

## Files

| File                                              | Purpose                                |
| ------------------------------------------------- | -------------------------------------- |
| `notebooks/keep_working_launcher.py`              | CLI entry point                        |
| `notebooks/keep_working.ipynb`                    | Interactive notebook with UI and tests |
| `notebooks/keep_working_systemd.service.template` | systemd user service template          |
| `notebooks/keep_working_history.json`             | JSON session log                       |
| `notebooks/keep_working_history.db`               | SQLite session log                     |
