# Browser Testing with Playwright

**IMPORTANT: Always use Playwright MCP tools for browser testing, not standalone test scripts.**
**IMPORTANT: When taking screenshots via Playwright MCP, always save them to `browser-testing/artifacts/` — never to the project root.**

When testing in the browser use Playwright (not headless) — minimal, copy-paste setup.
Saves screenshots, HTML snapshot, HAR (network), and captures console.log.

## Folder layout

- All artifacts go under: `browser-testing/artifacts/<seq>-<name>/`
- Test file lives under: `browser-testing/tests/<seq>-<name>.py`

## Test template

Save as: `tests/<seq>-<name>.py`

```python
import os, sys, time, traceback
from pathlib import Path
from playwright.sync_api import sync_playwright

# ==== CONFIG (edit per test) ====
TEST_SEQ = "001"
TEST_NAME = "login-flow"
URL = "https://example.com"
CLICK_TXT = "More information"  # or None
ASSERT_IN_TITLE = "Example"    # or None
# =================================

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / f"{TEST_SEQ}-{TEST_NAME}"
ART.mkdir(parents=True, exist_ok=True)

def ts():
    return time.strftime("%Y%m%d-%H%M%S")

def run():
    console_log_path = ART / "console.log"
    with sync_playwright() as p, console_log_path.open("a", encoding="utf-8") as clog:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_har_path=str(ART / "network.har"),
            record_har_mode="minimal"
        )
        page = context.new_page()

        def on_console(msg):
            line = f"[console.{msg.type}] {msg.text}\n"
            sys.stdout.write(line)
            clog.write(line)
        page.on("console", on_console)

        try:
            page.goto(URL, wait_until="domcontentloaded")
            if CLICK_TXT:
                page.get_by_text(CLICK_TXT).first.click()
            if ASSERT_IN_TITLE:
                assert ASSERT_IN_TITLE in page.title()
        except Exception:
            page.screenshot(path=str(ART / f"error-{ts()}.png"), full_page=True)
            (ART / f"page-{ts()}.html").write_text(page.content(), encoding="utf-8")
            traceback.print_exc()
            raise
        else:
            page.screenshot(path=str(ART / f"final-{ts()}.png"), full_page=True)
            (ART / f"page-{ts()}.html").write_text(page.content(), encoding="utf-8")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    run()
```

## Notes

- Headless is enabled (change to `headless=False` to watch it)
- Always diagnose what's actually on the page rather than assuming the UI structure
- Always check import ordering
