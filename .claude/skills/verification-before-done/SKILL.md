---
name: verification-before-done
description: |
  MANDATORY before signaling task completion. Ensures implemented features
  actually work through automated and visual verification. Auto-triggers on
  phrases like "done", "finished", "implemented", "completed", "ready to ship".
---

# Verification Before Done

**CRITICAL**: Never claim a task is "done" without completing this verification checklist.

## Why This Exists

Claude Code often claims something is "done" without actually testing it. This leads to:
- User finds it broken → "Fixed" → Something else broke → Repeat 5-10x
- Wasted time and frustration

## Mandatory Verification Steps

### 1. Run Relevant Tests

Choose based on what changed:

| Changed | Test Command | Must Pass |
|---------|--------------|-----------|
| API endpoint | `@api-tester` or curl | Yes |
| HTML template | `@curl-tester` or `/check-page` | Yes |
| User flow | `/chrome/test-flow` or `@e2e-tester` | Yes |
| Multiple components | `/test-all` | Yes |
| Background job | Check worker logs | Yes |

### 2. Visual/Manual Verification

At minimum, do ONE of these:
- `curl localhost:8006/<page>` - Check response AND JS console at bottom
- `/chrome/test-flow <description>` - Interactive browser check
- `/check-logs` - Quick console check

### 3. Verify No Regressions

If modifying existing code:
- Test the original functionality still works
- Test related features that might be affected

## Common Failure Modes

| What You Said | What You Should Have Verified |
|---------------|-------------------------------|
| "Page works" | Did you actually curl it and get 200? |
| "Form submits" | Did you check the database for the created record? |
| "Button works" | Did you test with Chrome tools? |
| "Fixed the bug" | Did you test the original reproduction steps? |
| "API returns data" | Did you verify the response JSON structure? |

## Output Format

**Before saying "done", ALWAYS include this table:**

```markdown
## Verification Results

| Check | Method | Result |
|-------|--------|--------|
| Page loads | curl localhost:8006/page | ✅ 200 |
| Form submits | Chrome test-flow | ✅ Data saved |
| No JS errors | Check console | ✅ Clean |
| Related feature X | curl | ✅ Still works |

✅ All verifications passed - task complete
```

## What NOT To Do

❌ Say "done" after only writing code
❌ Say "should work" without testing
❌ Say "fixed" without running reproduction steps
❌ Assume changes work because they "look right"
❌ Skip verification because "it's a small change"

## Quick Reference

**Minimum viable verification for ANY task:**

```bash
# Check page loads and no JS errors
curl -s localhost:8006/<page> | tail -100
```

The JS console output is at the bottom of every page response - check it!
