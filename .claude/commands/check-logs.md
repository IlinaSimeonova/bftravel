---
name: check-logs
description: Quick console + network check without screenshot (low token cost)
---

Check the page at the provided path for console errors and network issues.

Usage: `/check-logs /path/`

Example: `/check-logs /workflows/`

1. Run browser-testing/check.py WITHOUT --screenshot flag
2. Read the console.log file from artifacts/
3. Report any JavaScript errors or warnings found
4. Summarize console output and network requests

Token cost: ~500-1000 tokens (no image analysis)
