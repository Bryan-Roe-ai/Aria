#!/usr/bin/env python3
"""Health check alert system for auto-improve.

Monitors repo_health_automation status
and triggers alerts when issues are detected.
Supports multiple notification channels: stderr, email, Slack, GitHub issues.

Usage:
  python scripts/health_check_alerts.py --check-now
  python scripts/health_check_alerts.py --watch --interval 300
  python scripts/health_check_alerts.py --github-issue "REPO/OWNER"
"""

from __future__ import annotations

import argparse
import json
import os
import smtplib
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, TypedDict
from urllib.error import URLError

REPO_ROOT = Path(__file__).resolve().parent.parent
STATUS_FILE = REPO_ROOT / "data_out" / "repo_health_automation" / "status.json"
ALERT_LOG = REPO_ROOT / "data_out" / "health_check_alerts.json"


@dataclass
class HealthAlert:
    """Represents a health check alert."""

    timestamp: str
    cycle: int
    alert_type: str  # "failure", "degradation", "recovery"
    severity: str  # "low", "medium", "high", "critical"
    message: str
    affected_steps: list[str]
    remediation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "cycle": self.cycle,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "affected_steps": self.affected_steps,
            "remediation": self.remediation,
        }


class SMTPConfig(TypedDict):
    host: str
    port: int
    user: str
    password: str


def read_status() -> dict[str, Any] | None:
    """Read current health check status."""
    if not STATUS_FILE.exists():
        return None

    try:
        with open(STATUS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error reading status file: {e}", file=sys.stderr)
        return None


def detect_alerts(status: dict[str, Any]) -> list[HealthAlert]:
    """Detect alerts from health check status.

    Args:
        status: Current health check status

    Returns:
        List of detected alerts
    """
    alerts = []

    # Check for cycle failure
    if not status.get("succeeded", True):
        failed_steps = [
            step.get("name", "unknown")
            for step in status.get("steps", [])
            if not step.get("succeeded", True)
        ]

        alerts.append(
            HealthAlert(
                timestamp=datetime.now(UTC).isoformat(),
                cycle=status.get("cycle", 0),
                alert_type="failure",
                severity="high",
                message="Auto-improve health check cycle failed",
                affected_steps=failed_steps,
                remediation=(
                    f"Review failed steps: {', '.join(failed_steps)}. "
                    "Run `python run_automation.py --auto-improve` "
                    "locally to debug."
                ),
            )
        )

    # Check for performance degradation
    if status.get("duration_sec", 0) > 60:
        alerts.append(
            HealthAlert(
                timestamp=datetime.now(UTC).isoformat(),
                cycle=status.get("cycle", 0),
                alert_type="degradation",
                severity="medium",
                message=(
                    "Health check took "
                    f"{status['duration_sec']:.1f}s "
                    "(threshold: 60s)"
                ),
                affected_steps=[],
                remediation="Check for slow dependencies or network issues",
            )
        )

    return alerts


def format_alert_email(alert: HealthAlert) -> tuple[str, str]:
    """Format alert as email subject and body.

    Returns:
        (subject, body) tuple
    """
    severity_icon = {
        "low": "ℹ️",
        "medium": "⚠️",
        "high": "🚨",
        "critical": "🔴",
    }.get(alert.severity, "❓")

    subject = (
        f"{severity_icon} Aria Health Check Alert: "
        f"{alert.alert_type.upper()}"
    )

    affected_steps_text = (
        chr(10).join(f"  - {step}" for step in alert.affected_steps)
        if alert.affected_steps
        else "  (none)"
    )

    body = f"""
Auto-Improve Health Check Alert
================================

Severity: {alert.severity.upper()}
Type: {alert.alert_type}
Time: {alert.timestamp}
Cycle: {alert.cycle}

Message:
{alert.message}

Affected Steps:
{affected_steps_text}

Remediation:
{alert.remediation or "No specific remediation available"}

View full status:
  cat data_out/repo_health_automation/status.json | python -m json.tool

Repository: {REPO_ROOT}
"""

    return subject, body


def send_email_alert(
    alert: HealthAlert,
    recipient: str,
    smtp_config: SMTPConfig | None = None,
) -> bool:
    """Send alert via email.

    Args:
        alert: Alert to send
        recipient: Email recipient
        smtp_config: SMTP configuration from env vars.
            Uses SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS.

    Returns:
        True if sent successfully
    """
    if smtp_config is None:
        smtp_config = {
            "host": os.getenv("SMTP_HOST", "localhost"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "user": os.getenv("SMTP_USER", ""),
            "password": os.getenv("SMTP_PASS", ""),
        }

    if not smtp_config["host"]:
        print("SMTP not configured; skipping email alert", file=sys.stderr)
        return False

    try:
        subject, body = format_alert_email(alert)

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = smtp_config["user"] or "noreply@aria-platform.local"
        msg["To"] = recipient

        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            server.starttls()
            if smtp_config["user"]:
                server.login(smtp_config["user"], smtp_config["password"])
            server.send_message(msg)

        print(f"✉️  Email alert sent to {recipient}")
        return True
    except (OSError, ValueError, smtplib.SMTPException) as e:
        print(f"Failed to send email alert: {e}", file=sys.stderr)
        return False


def send_slack_alert(
    alert: HealthAlert,
    webhook_url: str | None = None,
) -> bool:
    """Send alert to Slack webhook.

    Args:
        alert: Alert to send
        webhook_url: Slack webhook URL (from env: SLACK_WEBHOOK_URL)

    Returns:
        True if sent successfully
    """
    if webhook_url is None:
        webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")

    if not webhook_url:
        return False

    try:
        import urllib.request

        severity_color = {
            "low": "#36a64f",
            "medium": "#ffa500",
            "high": "#ff0000",
            "critical": "#8b0000",
        }.get(alert.severity, "#808080")

        payload = {
            "attachments": [
                {
                    "color": severity_color,
                    "title": (
                        f"{alert.alert_type.upper()} - "
                        f"Cycle {alert.cycle}"
                    ),
                    "text": alert.message,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.upper()},
                        {
                            "title": "Affected Steps",
                            "value": ", ".join(alert.affected_steps)
                            or "(none)",
                        },
                        {
                            "title": "Remediation",
                            "value": alert.remediation or "Check logs",
                        },
                    ],
                    "footer": f"Aria Auto-Improve | {alert.timestamp}",
                }
            ]
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(req) as response:  # noqa: S310
            if response.status == 200:
                print("📱 Slack alert sent")
                return True
    except (OSError, URLError, ValueError) as e:
        print(f"Failed to send Slack alert: {e}", file=sys.stderr)

    return False


def log_alert(alert: HealthAlert) -> None:
    """Log alert to file."""
    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)

    alerts = []
    if ALERT_LOG.exists():
        try:
            with open(ALERT_LOG, encoding="utf-8") as f:
                alerts = json.load(f)
        except (OSError, json.JSONDecodeError):
            pass

    alerts.append(alert.to_dict())

    # Keep last 100 alerts
    alerts = alerts[-100:]

    try:
        with open(ALERT_LOG, "w", encoding="utf-8") as f:
            json.dump(alerts, f, indent=2)
    except OSError as e:
        print(f"Failed to log alert: {e}", file=sys.stderr)


def check_now(send_alerts: bool = True) -> int:
    """Check status now and send alerts if needed.

    Args:
        send_alerts: If True, send notifications for detected alerts

    Returns:
        0 if healthy, 1 if issues detected
    """
    status = read_status()
    if status is None:
        print("❓ No health check status found; run auto-improve first")
        return 2

    alerts = detect_alerts(status)

    if not alerts:
        print("✅ Health check is healthy")
        return 0

    print(f"⚠️  Detected {len(alerts)} alert(s):")
    for alert in alerts:
        print(f"  • [{alert.severity.upper()}] {alert.message}")
        log_alert(alert)

        if send_alerts:
            # Try to send to configured channels
            alert_email = os.getenv("ALERT_EMAIL")
            if alert_email:
                send_email_alert(alert, alert_email)
            send_slack_alert(alert)

    return 1


def watch_status(interval: int = 300) -> None:
    """Watch status file and alert on changes.

    Args:
        interval: Check interval in seconds
    """
    print(f"👁️  Watching health status (interval: {interval}s)...")
    print("Press Ctrl+C to stop")

    last_cycle = -1

    try:
        while True:
            status = read_status()
            if status and status.get("cycle", 0) != last_cycle:
                last_cycle = status.get("cycle", 0)
                check_now(send_alerts=True)

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n👋 Stopped watching")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Health check alert system for auto-improve"
    )
    parser.add_argument(
        "--check-now",
        action="store_true",
        help="Check status now and send alerts",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch status continuously",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Check interval in seconds (default: 300)",
    )
    parser.add_argument(
        "--no-alerts",
        action="store_true",
        help="Check but don't send notifications",
    )

    args = parser.parse_args()

    if args.watch:
        watch_status(interval=args.interval)
        return 0

    return check_now(send_alerts=not args.no_alerts)


if __name__ == "__main__":
    sys.exit(main())
