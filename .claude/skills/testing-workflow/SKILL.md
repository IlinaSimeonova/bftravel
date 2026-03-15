---
name: testing-workflow
description: |
  Choose the optimal testing strategy based on what was changed.
  Knows about all available testing commands and agents.
  Auto-triggers on: "test", "verify", "check if works", "not working", "broken".
---

# Testing Strategy Guide

## Decision Tree: What Test Method to Use?

```
What changed?
│
├── API endpoint only
│   └── Use: @api-tester + curl verification
│
├── HTML template / page
│   └── Use: @curl-tester (checks JS console too!)
│       └── Or: /chrome/test-flow for interactive check
│
├── User flow / multi-step process
│   └── Use: /chrome/test-flow (quick) OR @e2e-tester (thorough)
│
├── Background job / worker
│   └── Use: Check docker logs + /job-staging-analysis
│
├── Multiple components / full feature
│   └── Use: /test-all (orchestrates everything)
│
└── Quick sanity check
    └── Use: /check-logs (console only) or /check-page (full)
```

## Available Tools Reference

### Commands (invoke with `/command`)

| Command | Use When | Speed | Token Cost |
|---------|----------|-------|------------|
| `/test-all` | Feature complete, need full verification | Slow | High |
| `/chrome/test-flow <flow>` | Need visual check of user journey | Medium | Medium |
| `/chrome/record` | Need to create GIF of interaction | Slow | High |
| `/check-logs` | Quick console error check | Fast | Low |
| `/check-page` | Full page check + screenshot | Medium | Medium |
| `/deploy-staging` | Ready to deploy | Slow | Medium |
| `/job-staging-analysis` | Debug job on staging | Medium | Medium |

### Agents (invoked automatically by Claude)

| Agent | Use When | Creates |
|-------|----------|---------|
| `@api-tester` | Testing API endpoints | pytest files |
| `@curl-tester` | Testing HTML pages render | pytest files |
| `@e2e-tester` | Full user journey testing | Playwright tests + screenshots |
| `@test-master` | Audit test coverage/quality | Test improvements |
| `@pr-reviewer` | Before creating PR | Review feedback |
| `@chrome-live` | Interactive browser testing | - |
| `@playwright-live` | Interactive Playwright testing | - |

## Quick Verification (< 30 seconds)

For immediate feedback without full test suite:

```bash
# Check any page loads and has no JS errors
curl -s localhost:8006/<page> | tail -100

# Note: JS console.log output appears at the bottom of every page!
```

## Common Testing Scenarios

### "I just changed an API endpoint"

```bash
# Quick manual test
curl -s localhost:8006/api/<endpoint>/ | python -m json.tool

# Create proper tests
# Claude will use @api-tester automatically
```

### "I modified a template/HTML"

```bash
# Quick check
curl -s localhost:8006/<page> | tail -100

# Interactive check
/chrome/test-flow navigate to <page> and verify content
```

### "I implemented a multi-step form"

```bash
# Interactive test with screenshots
/chrome/test-flow fill form at <page> and submit

# Or full Playwright test suite
# Claude will use @e2e-tester automatically
```

### "Something is broken but I don't know what"

```bash
# Check console errors first
/check-logs

# Then check the specific page
curl -s localhost:8006/<broken-page> | tail -100

# Look for error patterns in the response
```

## The "It's Fixed" Trap

**NEVER say "fixed" after only changing code.**

You MUST:
1. Run the exact reproduction steps from the bug report
2. Verify the original issue is gone
3. Check that no new issues appeared
4. Test edge cases if applicable

See: `verification-before-done` skill for mandatory checklist.

## Test Output Locations

| Test Type | Output Location |
|-----------|-----------------|
| Playwright screenshots | `{app}/tests/e2e/*.png` |
| curl-tester files | `{app}/tests/test_*.py` |
| API test files | `{app}/tests/test_api_*.py` |
| Browser artifacts | `browser-testing/artifacts/` |
