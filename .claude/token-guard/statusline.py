#!/usr/bin/env python3
"""A zero-API-cost status line for Claude Code Token Guard."""
from __future__ import annotations

import json
import sys


def percent(value):
    try:
        return max(0, min(100, int(round(float(value)))))
    except (TypeError, ValueError):
        return 0


def number(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def fmt_tokens(value):
    value = number(value)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.0f}k"
    return str(value)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return

    model = data.get("model", {}).get("display_name") or data.get("model", {}).get("id") or "Claude"
    effort = data.get("effort")
    window = data.get("context_window") or {}
    used = percent(window.get("used_percentage"))
    usage = window.get("current_usage") or {}
    input_tokens = number(usage.get("input_tokens"))
    cache_tokens = number(usage.get("cache_read_input_tokens"))
    total_reads = input_tokens + cache_tokens
    cache_pct = round(cache_tokens / total_reads * 100) if total_reads else None

    filled = round(used / 10)
    bar = "#" * filled + "-" * (10 - filled)
    if used >= 90:
        action = "ACTION: /compact now"
    elif used >= 75:
        action = "ACTION: /compact focus on current task"
    elif used >= 55:
        action = "WATCH: finish task, then /clear"
    else:
        action = "healthy"

    parts = [f"[Token Guard] {model}"]
    if effort:
        parts.append(f"effort:{effort}")
    parts.append(f"ctx:{bar} {used}%")
    parts.append(f"in:{fmt_tokens(input_tokens)}")
    if cache_pct is not None:
        parts.append(f"cache:{cache_pct}%")
    parts.append(action)
    print(" | ".join(parts))


if __name__ == "__main__":
    main()
