---
name: ux-principle-tracker
description: |
  Tracks UI/UX remarks from the user during development conversations.
  When the user makes a correction, complaint, or preference about UI/UX,
  extracts the general principle and appends it to CLAUDE.md.
  Auto-triggers on UI/UX feedback like: "too much whitespace", "should be aligned",
  "wrong color", "move this", "this looks bad", "don't put X here",
  "I don't like", "buttons should", "make it", "that's ugly", "spacing is off".
---

# UX Principle Tracker

## Purpose

Capture UI/UX preferences and corrections from the user as permanent principles in CLAUDE.md, so the same mistakes are never repeated.

## When to Trigger

Activate when the user makes a remark that is a UI/UX opinion, correction, or preference during any task. Examples:

- "There's too much whitespace here" → Layout principle
- "Put the button on the right" → Actions principle
- "Don't use that color" → Style principle
- "This page is too cluttered" → Layout principle
- "The tabs should be at the top" → Navigation principle
- "Why is this so small?" → Layout/Style principle
- "I don't want modals for this" → Interaction principle
- "Labels should be above inputs" → Forms principle

## Workflow

### Step 1: Detect the Remark

When the user says something that sounds like a UI/UX preference or correction, pause and extract it.

### Step 2: Formulate the Principle

Convert the specific remark into a **general, reusable principle**. Rules:

- Make it context-independent (not "on the dashboard page" but "on list pages")
- Make it actionable (start with a verb or "Never/Always")
- Keep it to one line (one dash-bullet in markdown)
- Don't duplicate existing principles — read the current section first

**Examples:**
| User Said | Extracted Principle |
|-----------|-------------------|
| "This has too much padding" | "Minimize padding — dense layouts over airy ones. Content should feel compact." |
| "Put actions on the right side" | "Action buttons go on the right side of their container, aligned with reading flow." |
| "I don't want modals for simple confirmations" | "Prefer inline confirmations over modals for simple yes/no actions." |
| "Tab labels are too generic" | "Tab labels must be specific to content, never generic ('Details', 'Info', 'Other')." |

### Step 3: Determine the Section

Place the principle in the correct existing section of CLAUDE.md under `# UI/UX Principles`:

| Section | Topics |
|---------|--------|
| `## Layout` | Spacing, padding, columns, alignment, density, sizing |
| `## Navigation` | Tabs, routes, breadcrumbs, back links, menu structure |
| `## Naming` | Labels, headings, tab names, button text |
| `## Content` | Data display, information hierarchy, empty/loading states |
| `## Actions` | Buttons, forms, confirmations, destructive actions |
| `## Principles to add` → `### General UI Rules` | Anything that doesn't fit above, or cross-cutting concerns |

If a principle doesn't fit any existing section, add a **new subsection** under `## Principles to add` with an appropriate heading (e.g., `### Forms`, `### Style`, `### Interactions`).

### Step 4: Add to CLAUDE.md

1. Read the target section from `/Users/pp/www/bigbongo/CLAUDE.md`
2. Check for duplicates or near-duplicates
3. Append the new principle as a bullet point at the end of the appropriate section
4. Use the Edit tool — do NOT rewrite the whole file

### Step 5: Confirm

Tell the user briefly:
```
Added UX principle to CLAUDE.md [{section}]: "{principle}"
```

## Important

- **Don't interrupt the user's main task.** Extract the principle and add it quickly, then continue with whatever they asked for.
- **Don't ask for confirmation** before adding. Just add it and mention what you did. The user can always ask to remove it.
- **One remark = one principle.** If the user makes multiple UI remarks, add each as a separate bullet.
- **Skip if already covered.** If an existing principle already captures the same idea, don't add a duplicate.
