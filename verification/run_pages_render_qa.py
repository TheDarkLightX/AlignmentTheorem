#!/usr/bin/env python3
"""Render the public GitHub Pages source at desktop and mobile widths.

This is source/render QA, not a production deployment attestation. The live
post-merge URL is checked separately after GitHub Pages deploys from `main`.
"""

from __future__ import annotations

import http.server
import json
import socketserver
import threading
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = ROOT / "verification" / "receipts" / "pages_render_qa.json"
SHOTS = ROOT / "verification" / "receipts" / "pages_screenshots"
PORT = 8765
PAGES = (
    "index.html",
    "data-center-social-contract.html",
    "v1-1-hyperdeflationary-alignment.html",
    "alignment-theorem-deep-dive.html",
)
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1000},
    "mobile": {"width": 390, "height": 844},
}


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def run() -> dict[str, object]:
    failures: list[str] = []
    reports: dict[str, object] = {}
    SHOTS.mkdir(parents=True, exist_ok=True)

    handler = lambda *args, **kwargs: QuietHandler(
        *args, directory=str(DOCS), **kwargs
    )
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                for viewport_name, viewport in VIEWPORTS.items():
                    context = browser.new_context(
                        viewport=viewport, device_scale_factor=1
                    )
                    context.emulate_media(reduced_motion="reduce")
                    for page_name in PAGES:
                        page = context.new_page()
                        console_errors: list[str] = []
                        page_errors: list[str] = []
                        page.on(
                            "console",
                            lambda msg, dest=console_errors: (
                                dest.append(msg.text)
                                if msg.type == "error"
                                else None
                            ),
                        )
                        page.on(
                            "pageerror",
                            lambda exc, dest=page_errors: dest.append(str(exc)),
                        )
                        url = f"http://127.0.0.1:{PORT}/{page_name}"
                        response = page.goto(url, wait_until="networkidle")
                        key = f"{viewport_name}:{page_name}"
                        status = response.status if response else None
                        title = page.title()
                        h1_count = page.locator("h1").count()
                        body_metrics = page.evaluate(
                            """() => ({
                              scrollWidth: document.documentElement.scrollWidth,
                              clientWidth: document.documentElement.clientWidth,
                              scrollHeight: document.documentElement.scrollHeight,
                              clientHeight: document.documentElement.clientHeight
                            })"""
                        )
                        horizontal_overflow = (
                            body_metrics["scrollWidth"]
                            > body_metrics["clientWidth"] + 2
                        )
                        main_visible = (
                            page.locator("main").count() > 0
                            and page.locator("main").first.is_visible()
                        )
                        local_link_failures: list[dict[str, object]] = []
                        hrefs = page.locator("a[href]").evaluate_all(
                            "els => els.map(e => e.getAttribute('href'))"
                        )
                        checked: set[str] = set()
                        for href in hrefs:
                            if not href or href.startswith(
                                ("#", "mailto:", "javascript:")
                            ):
                                continue
                            target = urljoin(url, href)
                            parsed = urlparse(target)
                            if (
                                parsed.netloc != f"127.0.0.1:{PORT}"
                                or target in checked
                            ):
                                continue
                            checked.add(target)
                            request = context.request.get(target)
                            if request.status >= 400:
                                local_link_failures.append(
                                    {"url": target, "status": request.status}
                                )

                        focus_outline_ok = True
                        if page.locator("a[href]").count():
                            first_link = page.locator("a[href]").first
                            first_link.focus()
                            focus_outline_ok = first_link.evaluate(
                                """el => {
                                  const s = getComputedStyle(el);
                                  return !(s.outlineStyle === 'none' ||
                                           s.outlineWidth === '0px');
                                }"""
                            )

                        report = {
                            "status": status,
                            "title": title,
                            "h1_count": h1_count,
                            "main_visible": main_visible,
                            "horizontal_overflow": horizontal_overflow,
                            "body_metrics": body_metrics,
                            "console_errors": console_errors,
                            "page_errors": page_errors,
                            "local_link_failures": local_link_failures,
                            "focus_outline_ok": focus_outline_ok,
                        }
                        reports[key] = report

                        if status != 200:
                            failures.append(f"{key}: HTTP {status}")
                        if not title or h1_count != 1 or not main_visible:
                            failures.append(
                                f"{key}: missing title, unique h1, or visible main"
                            )
                        if horizontal_overflow:
                            failures.append(
                                f"{key}: horizontal overflow {body_metrics}"
                            )
                        if console_errors or page_errors:
                            failures.append(f"{key}: browser errors")
                        if local_link_failures:
                            failures.append(
                                f"{key}: dead local links {local_link_failures}"
                            )
                        if page_name == "index.html" and not focus_outline_ok:
                            failures.append(
                                f"{key}: no visible keyboard focus outline"
                            )

                        page.screenshot(
                            path=str(
                                SHOTS
                                / f"{viewport_name}-{page_name.replace('.html','')}.png"
                            ),
                            full_page=True,
                        )
                        page.close()

                    calc = context.new_page()
                    calc.goto(
                        f"http://127.0.0.1:{PORT}/data-center-social-contract.html",
                        wait_until="networkidle",
                    )
                    ranges = calc.locator('input[type="range"]')
                    range_count = ranges.count()
                    before = calc.locator("body").inner_text()
                    for index in range(range_count):
                        slider = ranges.nth(index)
                        max_value = slider.get_attribute("max")
                        if max_value is not None:
                            slider.fill(max_value)
                            slider.dispatch_event("input")
                            slider.dispatch_event("change")
                    after = calc.locator("body").inner_text()
                    calc_ok = range_count > 0 and before != after
                    reports[f"{viewport_name}:calculator"] = {
                        "range_count": range_count,
                        "content_changed": before != after,
                        "passed": calc_ok,
                    }
                    if not calc_ok:
                        failures.append(
                            f"{viewport_name}: calculator did not respond"
                        )
                    calc.close()
                    context.close()
                browser.close()
        finally:
            server.shutdown()
            thread.join(timeout=5)

    result = {
        "schema": "alignment-theorem-pages-render-qa-v1",
        "pages": list(PAGES),
        "viewports": VIEWPORTS,
        "reports": reports,
        "failures": failures,
        "passed": not failures,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)
