import argparse
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import Browser, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "figures" / "ui"


def launch(p) -> Browser:
    try:
        return p.chromium.launch(channel="chrome")
    except Exception:
        return p.chromium.launch()  # needs `python -m playwright install chromium`


def shoot(url: str, tag: str, widths: list[int]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = launch(p)
        for w in widths:
            ctx = browser.new_context(viewport={"width": w, "height": 900}, device_scale_factor=1 if w > 800 else 2)
            page = ctx.new_page()
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector(".nh-footer", timeout=30000)
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(3000)
            h = page.evaluate("() => Math.max(...[...document.querySelectorAll('*')].map(e => e.scrollHeight))")
            page.set_viewport_size({"width": w, "height": min(int(h) + 40, 6000)})
            page.wait_for_timeout(1500)
            path = OUT / f"{tag}_{w}.png"
            page.screenshot(path=str(path), full_page=True)
            overflow = page.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
            print(f"{path.relative_to(ROOT)}  horizontal overflow {overflow}px")
            ctx.close()
        browser.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the app headless and screenshot a page at laptop and phone width")
    ap.add_argument("--page", default="", help="URL path, e.g. Screen; empty = Home")
    ap.add_argument("--tag", default="home")
    ap.add_argument("--port", type=int, default=8599)
    ap.add_argument("--widths", type=int, nargs="+", default=[1440, 390])
    args = ap.parse_args()
    server = subprocess.Popen([sys.executable, "-m", "streamlit", "run", str(ROOT / "app" / "Home.py"),
                               "--server.headless", "true", "--server.port", str(args.port)],
                              cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(5)
        shoot(f"http://localhost:{args.port}/{args.page}", args.tag, args.widths)
    finally:
        server.terminate()


if __name__ == "__main__":
    main()
