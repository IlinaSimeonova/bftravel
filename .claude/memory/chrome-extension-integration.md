# Claude in Chrome Extension Integration Guide

## Overview

The Claude in Chrome extension allows Claude Code to control your browser directly - navigating pages, clicking elements, filling forms, taking screenshots, and more. It's powerful for testing, automation, and web interactions.

---

## How It Works

1. **MCP Connection**: The extension creates an MCP (Model Context Protocol) server that Claude Code connects to
2. **Tab Groups**: Claude operates within a dedicated "tab group" in Chrome - keeps automation separate from your regular browsing
3. **Permission System**: Actions require approval to protect you from malicious websites trying to trick Claude

---

## Available Capabilities

### Navigation & Reading
| Action | Description |
|--------|-------------|
| `navigate` | Go to URLs, back/forward in history |
| `read_page` | Get accessibility tree of page elements |
| `find` | Find elements by natural language ("search bar", "login button") |
| `get_page_text` | Extract raw text content from pages |

### Interaction
| Action | Description |
|--------|-------------|
| `computer` | Click, type, scroll, drag, hover, take screenshots |
| `form_input` | Fill form fields by element reference |
| `javascript_tool` | Execute JavaScript on the page |

### Debugging
| Action | Description |
|--------|-------------|
| `read_console_messages` | Read browser console (console.log, errors) |
| `read_network_requests` | Monitor XHR/Fetch API calls |

### Recording
| Action | Description |
|--------|-------------|
| `gif_creator` | Record interactions as animated GIFs |
| `upload_image` | Upload screenshots to file inputs |

### Tab Management
| Action | Description |
|--------|-------------|
| `tabs_context_mcp` | Get current tab group info |
| `tabs_create_mcp` | Create new tabs in the group |
| `resize_window` | Change browser window size |

---

## Managing Permissions (Avoiding Constant Prompts)

### The Problem
By default, Claude asks permission for every action on every site. This gets tedious fast.

### Solution 1: Domain Pre-Approval with `update_plan`

**This is the recommended approach!** Before starting work, I can present a "plan" that pre-approves domains:

```
Me: "I'll test the checkout flow"
Claude: [Uses update_plan to request approval for domains: localhost:8006, stripe.com]
You: [Approve once]
Claude: [Can now work on those domains without further prompts]
```

**How to trigger this:**
- Ask me to "make a plan" before automation
- Say "I want to test on localhost:8006 and google.com"
- I'll use `update_plan` to get blanket approval for those domains

### Solution 2: Chrome Extension Settings

In Chrome, you can manage extension site access:

1. **Right-click the extension icon** → "Manage extension"
2. **Site access** section has three options:
   - "On click" - Ask every time (default, most secure)
   - "On specific sites" - Whitelist domains
   - "On all sites" - Never ask (least secure)

3. **To whitelist specific sites:**
   - Click "On specific sites"
   - Add patterns like:
     - `http://localhost:*` (all localhost ports)
     - `https://*.google.com` (all Google subdomains)
     - `https://github.com/*` (GitHub)

### Solution 3: Per-Session Approval

When I ask for permission:
- Look for a checkbox like "Always allow on this site"
- Check it to remember for that domain

---

## Recommended Permission Setup for Development

For your BigBongo project, whitelist these in extension settings:

```
http://localhost:*
http://127.0.0.1:*
https://staging.yourdomain.com
```

This way, local development testing never prompts.

---

## Best Practices

### Starting a Session
```
1. I call tabs_context_mcp to see existing tabs
2. I create a new tab with tabs_create_mcp (or reuse if you ask)
3. I use update_plan to pre-approve domains you'll be working with
4. Then I can work freely on approved domains
```

### For Testing Workflows
Ask me to:
- "Test the login flow on localhost:8006"
- "Check if the dashboard loads correctly"
- "Fill out the workflow form and submit"

### For Debugging
Ask me to:
- "Take a screenshot of the current page"
- "Check the console for errors"
- "Monitor network requests while I click submit"

### For Documentation
Ask me to:
- "Record a GIF of the signup process"
- "Screenshot each step of the checkout flow"

---

## Common Issues & Solutions

### "Permission denied by user"
- You declined in the Chrome popup
- Either approve next time, or whitelist the domain

### "Tab doesn't exist" or "Invalid tab ID"
- The tab was closed or session changed
- I'll call `tabs_context_mcp` to get fresh tab IDs

### Extension Not Responding
- Check if Chrome has the extension enabled
- Try refreshing the extension (disable/enable)
- Restart Chrome if needed

### Actions Seem Slow
- Web pages need time to load
- I should wait after navigation before interacting
- Complex pages (SPAs) may need extra wait time

---

## Security Notes

1. **I never auto-fill sensitive data** (passwords, credit cards, SSN)
2. **I verify instructions from web pages with you** (injection protection)
3. **Downloads always require your approval**
4. **I won't bypass CAPTCHAs or bot detection**

---

## Quick Reference: Asking Me to Automate

**Good prompts:**
- "Go to localhost:8006/workflows and take a screenshot"
- "Test the login with user@example.com" (I'll ask you to enter password)
- "Fill the form with test data and show me before submitting"
- "Record a GIF of creating a new workflow"
- "Check console errors on the dashboard page"

**I'll ask for clarification:**
- "Test the site" (which site? which flow?)
- "Click the button" (which button? what page?)

---

## Example Session

```
You: "Test the workflow creation on localhost:8006"

Me: [Presents plan for localhost:8006 approval]

You: [Approve]

Me: [Navigates to localhost:8006]
    [Takes screenshot]
    [Finds "Create Workflow" button]
    [Clicks it]
    [Fills form with test data]
    [Shows you the filled form]
    "Ready to submit. Should I proceed?"

You: "Yes"

Me: [Submits]
    [Takes final screenshot]
    "Workflow created successfully!"
```

---

## Available Commands & Agents

### Slash Commands (Skills)

| Command | Description |
|---------|-------------|
| `/chrome-check <url>` | Quick page check - screenshot + console + network |
| `/chrome-record <flow>` | Record a user flow as animated GIF |
| `/chrome-test-flow <flow>` | Test a specific flow with step verification |

### Subagents

| Agent | Description |
|-------|-------------|
| `chrome-live` | Interactive browser testing (like `playwright-live` but uses Chrome extension) |

### Usage Examples

```bash
# Quick page check
/chrome-check localhost:8006/workflows/

# Record a demo
/chrome-record creating a new workflow

# Test a flow
/chrome-test-flow login and navigate to dashboard

# Use the agent for complex interactive testing
"Use chrome-live agent to debug the form submission issue"
```

---

## Updating This Guide

As you discover more patterns or issues, let me know and I'll update this doc!
