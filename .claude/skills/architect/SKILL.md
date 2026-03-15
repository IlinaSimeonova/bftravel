---
name: architect
description: |
  Auto-triggers when a technical decision needs to be made during feature implementation.
  Pauses work, researches options, and presents a short non-technical explanation with
  pros/cons and a recommendation. Waits for user approval before proceeding.
  Triggers on: choosing between libraries, APIs, services, database designs, architecture
  patterns, third-party integrations, or any implementation approach where multiple
  valid paths exist.
---

# Architect — Technical Decision Gate

## When This Triggers

You MUST activate this skill when implementing a feature requires choosing between:

- **Services**: SQS vs Django-Q2 vs Celery, REST vs WebSocket, etc.
- **Integration approach**: API key vs SDK vs Agent, webhook vs polling, etc.
- **Data design**: New model vs extending existing, relational vs JSON field, etc.
- **Architecture**: Sync vs async, monolith vs service, queue vs cron, etc.
- **Third-party tools**: Which library, which provider, which tier
- **Frontend approach**: New page vs modal vs inline, separate view vs HTMX, etc.
- **Any fork in the road** where the choice affects future development

Do NOT trigger for trivial choices (variable naming, import order, minor refactors).

## How It Works

### Step 1: Stop Implementation

The moment you identify a decision point, **stop coding**. Do not make the choice silently.

### Step 2: Research (If Needed)

- Read relevant parts of the codebase to understand existing patterns
- Check what's already in `requirements.txt` or the project stack
- Consider the project's scale, team size (small), and hosting (single VPS with Nginx/Gunicorn)
- Use web search if comparing external services or libraries

### Step 3: Present the Decision

Use this format — keep it short and non-technical:

```
## Decision needed: [one-line summary]

**What we're solving**: [1-2 sentences explaining the need in plain language]

**Options**:

1. **[Option A name]** — [1 sentence what it does]
   - Good: [1-2 bullet points]
   - Bad: [1-2 bullet points]

2. **[Option B name]** — [1 sentence what it does]
   - Good: [1-2 bullet points]
   - Bad: [1-2 bullet points]

(add Option C only if genuinely relevant)

**My recommendation**: [Option X] — [1 sentence why]
```

### Step 4: Wait

Do not proceed until the user responds. They may:
- Approve the recommendation
- Pick a different option
- Ask for more detail on a specific option
- Suggest something else entirely

If they ask for more detail, provide it — but only for what they asked about.

## Rules

- **Keep it simple**. The user is not a developer. Avoid jargon. If you must use a technical term, explain it in parentheses.
- **Be opinionated**. Always make a clear recommendation. Don't say "it depends" without picking one.
- **Be honest about trade-offs**. Don't hide downsides to push your preferred option.
- **Consider what's already in the project**. If Django-Q2 is already installed, don't recommend Celery without good reason.
- **Think about the server**. This runs on a single VPS — don't recommend solutions that need complex infrastructure.
- **Max 2-3 options**. Don't overwhelm with 5 choices. Filter down to the real contenders.
- **No implementation until approved**. This is a hard stop, not a suggestion.
