"""Sync latest AI report from repo to desktop.

Run this after GitHub Actions has generated the daily report.
Usage:
    python sync_desktop.py              # sync latest
    python sync_desktop.py 2026-06-10   # sync specific date
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
REPORTS_DIR = ROOT / "reports"
DESKTOP_DIR = Path.home() / "Desktop" / "每日AI热点总结报告"


def date_to_desktop_name(date_str: str) -> str:
    """Convert '2026-06-10' to '26.6.10AI热点总结.md'"""
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{d.year % 100}.{d.month}.{d.day}AI热点总结.md"


def find_latest_report() -> Path | None:
    md_files = sorted(REPORTS_DIR.glob("*.md"))
    return md_files[-1] if md_files else None


def main():
    import subprocess

    # 1. Git pull
    print("[sync] git pull...")
    result = subprocess.run(
        ["git", "pull"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout.strip())
    if result.returncode != 0:
        print(f"WARNING: git pull failed: {result.stderr}")

    # 2. Find source report
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
        src = REPORTS_DIR / f"{date_str}.md"
    else:
        src = find_latest_report()
        if not src:
            print("ERROR: No reports found in", REPORTS_DIR)
            sys.exit(1)
        date_str = src.stem

    if not src.exists():
        print(f"ERROR: Report not found: {src}")
        sys.exit(1)

    # 3. Copy to desktop
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    dst_name = date_to_desktop_name(date_str)
    dst = DESKTOP_DIR / dst_name

    shutil.copy2(src, dst)
    print(f"[sync] {src.name} → 桌面/{dst_name}")


if __name__ == "__main__":
    main()
