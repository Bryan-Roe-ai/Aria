# AGI Launcher — VS Code Task & User Service

The AGI launcher (`scripts/startup_agi.sh`) starts the local supporting services
(Azurite + Azure Functions host) and polls `/api/agi/status` in repeating
cycles. You can run it interactively from VS Code, or install it as a
**systemd user service** so it runs in the background and restarts on failure.

## Launcher options

| Flag | Env override | Default | Meaning |
| ---------------------- | ---------------------- | ------- | ------------------------------------------ |
| `--cycles N` | `AGI_LAUNCH_CYCLES` | `1` | Number of launcher cycles (`0` = infinite) |
| `--short-break-sec N` | `AGI_SHORT_BREAK_SEC` | `30` | Sleep between normal cycles |
| `--long-break-sec N` | `AGI_LONG_BREAK_SEC` | `300` | Sleep after every long-break interval |
| `--long-break-every N` | `AGI_LONG_BREAK_EVERY` | `5` | Take the long break every N cycles |

## Run via VS Code task

`Terminal → Run Task… → startup: agi`

The task prompts for each of the four options (press Enter to accept the
default) and runs the launcher in a dedicated terminal panel.

## Run as a user service

Four tasks manage a `systemd --user` service defined in
`config/aria-agi-launcher.service` (defaults to `AGI_LAUNCH_CYCLES=0`, i.e.
runs forever):

| Task | Action |
| ---------------------- | ---------------------------------------------------------------------------- |
| `service: agi install` | Copy the unit to `~/.config/systemd/user/`, `daemon-reload`, and `enable` it |
| `service: agi start` | Start the service and print its status |
| `service: agi stop` | Stop the service |
| `service: agi status` | Show status and the last 30 log lines |

Equivalent manual commands:

```bash
# Install / refresh
mkdir -p "$HOME/.config/systemd/user"
cp config/aria-agi-launcher.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now aria-agi-launcher.service

# Inspect
systemctl --user status aria-agi-launcher.service
journalctl --user -u aria-agi-launcher.service -f

# Stop
systemctl --user stop aria-agi-launcher.service
```

### Tuning the service

Edit the `Environment=` lines in `config/aria-agi-launcher.service`, re-run the
`service: agi install` task, then restart with `service: agi start`.

### Notes

- **The user service needs a running systemd user manager.** Many dev
  containers (including this workspace) do not run systemd — there the
  `service: agi *` tasks will report that the user manager is unavailable; use
  the `startup: agi` task instead, or install the service on a host/VM with
  systemd.
- The unit uses absolute paths under `/workspaces/Aria`; adjust
  `WorkingDirectory`, `ExecStart`, and the log paths if your checkout lives
  elsewhere.
- To keep a user service running after you log out, enable lingering once:
  `loginctl enable-linger "$USER"`.
- Logs also go to `data_out/aria-agi-launcher.service.log` and
  `data_out/aria-agi-launcher.service_error.log`.
