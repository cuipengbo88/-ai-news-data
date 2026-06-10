from playwright.sync_api import sync_playwright
import os
import sys
from datetime import datetime, timedelta

# If called with a date arg, use it; otherwise use today
if len(sys.argv) > 1:
    date = sys.argv[1]
else:
    date = datetime.now().strftime('%Y-%m-%d')

url = f'https://aihot.virxact.com/{date}'

# Use relative path from repo root, fallback to user home on Windows
import pathlib
script_dir = pathlib.Path(__file__).parent.resolve()
out_dir = script_dir / 'raw'
os.makedirs(out_dir, exist_ok=True)
out_path = out_dir / f'{date}.txt'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(2000)

    skip_btn = page.locator('text=暂不登录').first
    if skip_btn.count() > 0:
        skip_btn.click()
        page.wait_for_timeout(3000)

    text = page.inner_text('body')
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # If date route returned thin content, fall back to /all
    if len(lines) < 20:
        page.goto('https://aihot.virxact.com/all', wait_until='networkidle', timeout=60000)
        page.wait_for_timeout(3000)
        skip_btn = page.locator('text=暂不登录').first
        if skip_btn.count() > 0:
            skip_btn.click()
            page.wait_for_timeout(3000)
        text = page.inner_text('body')
        lines = [l.strip() for l in text.split('\n') if l.strip()]

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Saved: {len(lines)} lines, {sum(len(l) for l in lines)} chars → {out_path}')

    browser.close()
