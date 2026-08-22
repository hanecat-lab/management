#!/usr/bin/env python3
"""Compact, local-only real-time status dashboard for Claude Code.

Claude Code sends one JSON session snapshot on stdin. This script turns supported
fields into a two-line dashboard. It makes no network calls and retains no data.
"""
from __future__ import annotations

import json
import sys

RESET = "\033[0m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"


def number(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def percentage(value: object) -> int:
    try:
        return max(0, min(100, int(round(float(value)))))
    except (TypeError, ValueError):
        return 0


def money(value: object) -> str:
    try:
        return f"${float(value):.4f}"
    except (TypeError, ValueError):
        return "--"


def tokens(value: object) -> str:
    value = number(value)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}k"
    return str(value)


def duration(value: object) -> str:
    milliseconds = number(value)
    if not milliseconds:
        return "--"
    seconds = milliseconds // 1000
    return f"{seconds // 60}m{seconds % 60:02d}s"


def bar(value: int, width: int = 16) -> str:
    filled = round(width * value / 100)
    return "█" * filled + "░" * (width - filled)


def health_color(context_percentage: int) -> str:
    if context_percentage >= 90:
        return RED
    if context_percentage >= 75:
        return YELLOW
    return GREEN


def action(context_percentage: int) -> str:
    if context_percentage >= 90:
        return "COMPACT NOW"
    if context_percentage >= 75:
        return "COMPACT (focus current task)"
    if context_percentage >= 55:
        return "Finish task → /clear"
    return "Healthy"


def get_rate_limit(data: dict[str, object], key: str) -> str | None:
    limits = data.get("rate_limits")
    if not isinstance(limits, dict):
        return None
    window = limits.get(key)
    if not isinstance(window, dict):
        return None
    used = window.get("used_percentage")
    if used is None:
        return None
    return f"{key}:{percentage(used)}%"


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return
    if not isinstance(data, dict):
        return

    model = data.get("model") if isinstance(data.get("model"), dict) else {}
    model_name = model.get("display_name") or model.get("id") or "Claude"
    effort = data.get("effort") or "--"

    context = data.get("context_window") if isinstance(data.get("context_window"), dict) else {}
    usage = context.get("current_usage") if isinstance(context.get("current_usage"), dict) else {}
    used = percentage(context.get("used_percentage"))
    input_tokens = number(usage.get("input_tokens"))
    cache_creation = number(usage.get("cache_creation_input_tokens"))
    cache_read = number(usage.get("cache_read_input_tokens"))
    total_input = input_tokens + cache_creation + cache_read
    cache_ratio = round(cache_read * 100 / total_input) if total_input else 0
    recent_output = number(context.get("total_output_tokens"))

    cost = data.get("cost") if isinstance(data.get("cost"), dict) else {}
    session_cost = money(cost.get("total_cost_usd"))
    session_duration = duration(cost.get("total_duration_ms"))

    color = health_color(used)
    print(f"{DIM}┌─ Claude Code Token Dashboard ─────────────────────────────{RESET}")
    print(
        f"{DIM}│{RESET} {model_name} · effort:{effort} · "
        f"ctx {color}{bar(used)} {used:>3}%{RESET} · {color}{action(used)}{RESET}"
    )
    print(
        f"{DIM}│{RESET} input:{tokens(input_tokens)} · cache read:{tokens(cache_read)} ({cache_ratio}%) · "
        f"cache write:{tokens(cache_creation)} · latest output:{tokens(recent_output)}"
    )
    final_parts = [f"session cost:{session_cost}", f"elapsed:{session_duration}"]
    final_parts.extend(filter(None, [get_rate_limit(data, "five_hour"), get_rate_limit(data, "seven_day")]))
    print(f"{DIM}│{RESET} " + " · ".join(final_parts))
    print(f"{DIM}└────────────────────────────────────────────────────────{RESET}")


if __name__ == "__main__":
    main()
