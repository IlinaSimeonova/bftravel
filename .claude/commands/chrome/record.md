---
name: chrome-record
description: Record a user flow as animated GIF using Claude in Chrome extension
---

Record a specific user flow as an animated GIF for documentation or bug reports.

Usage: `/chrome-record <description of flow>`

Examples:
- `/chrome-record workflow creation flow`
- `/chrome-record login and navigate to dashboard`
- `/chrome-record form validation errors`

## Steps

1. **Setup browser**
   - `tabs_context_mcp` with `createIfEmpty: true`
   - Create new tab if needed

2. **Pre-approve domains**
   - `update_plan` with domains and flow description
   - Wait for user approval

3. **Start recording**
   - `gif_creator` with `action: start_recording`
   - Take initial screenshot immediately

4. **Perform the flow**
   - Navigate to starting page
   - Execute each step of the flow
   - Take extra screenshots at key moments
   - Use `wait` between actions for smooth playback

5. **Stop recording**
   - Take final screenshot
   - `gif_creator` with `action: stop_recording`

6. **Export GIF**
   - `gif_creator` with `action: export, download: true`
   - Use descriptive filename like `workflow-creation-2025-01-05.gif`

## Recording Tips

- **Before each action**: Take a screenshot to ensure the "before" state is captured
- **After each action**: Wait 0.5-1 second, then screenshot the "after" state
- **Smooth playback**: More frames = smoother animation but larger file

## Example Flow Script

```
1. tabs_context_mcp(createIfEmpty: true) → tabId

2. update_plan(domains: ["localhost:8006"], approach: ["Record workflow creation"])

3. gif_creator(action="start_recording", tabId=X)

4. navigate(url="localhost:8006/workflows/", tabId=X)

5. computer(action="screenshot", tabId=X)  // Initial state

6. computer(action="wait", duration=1, tabId=X)

7. find(query="create workflow button", tabId=X) → ref

8. computer(action="screenshot", tabId=X)  // Before click

9. computer(action="left_click", ref=Y, tabId=X)

10. computer(action="wait", duration=1, tabId=X)

11. computer(action="screenshot", tabId=X)  // After click

12. [Continue flow...]

13. computer(action="screenshot", tabId=X)  // Final state

14. gif_creator(action="stop_recording", tabId=X)

15. gif_creator(action="export", download=true, filename="workflow-creation.gif", tabId=X)
```

## GIF Options

When exporting, you can customize:
- `showClickIndicators`: Orange circles at click locations (default: true)
- `showDragPaths`: Red arrows for drag actions (default: true)
- `showActionLabels`: Black labels describing actions (default: true)
- `showProgressBar`: Orange progress bar at bottom (default: true)
- `showWatermark`: Claude logo watermark (default: true)
- `quality`: 1-30, lower = better quality (default: 10)

## Output

- GIF downloaded to browser's download folder
- Report what was recorded and filename

## Token Cost
~5000-15000 tokens depending on flow length
