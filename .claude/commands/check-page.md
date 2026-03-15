---
name: check-page
description: Full visual check with screenshot + console + network (higher token cost)
---

Check the page at the provided path with full visual analysis including screenshot.

Usage: `/check-page /path/`

Example: `/check-page /workflows/`

1. Run browser-testing/check.py WITH --screenshot flag
2. Read screenshot, console.log, network.har, and HTML files
3. Analyze visual appearance for rendering issues
4. Report any JavaScript errors or warnings found
5. Summarize both visual and console issues

Token cost: ~8000 tokens (includes image analysis)
