# CLAUDE.md
@.claude-pilot/map.md
@CLAUDE-NONDEV.md
@specs/CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Skills (Auto-Triggered)

- **Architect** (`.claude/skills/architect/SKILL.md`): Activates automatically when a technical decision needs to be made. Stops work, presents options in plain language, waits for approval. MUST trigger before making any architectural or technology choice.

## General Behavior & Workflow

- Be brief in answers.
- Answer detailed but short. we don't need long paragraphs and much code in advance
- output a smiley emoji if you think you have completed the task successfully
- be very careful with determining whether I want just information or implementation. don't be overzealous to make changes to code. Follow my instructions and output only if I want information.
- If asked to show code before changing files, do not change files
- If asked to suggest possible solutions, do not change files
- Always determine if changes are requested or just suggestions are needed
- do not create fallback methods for things and also do not create legacy versions of old things.
- When introducing improvements and fixes and new methods, always cleanup and delete the old leftovers that are no longer going to be used and not needed. Default behavior should be NOT to do any fallbacks, unless explicitly requested. Don't leave me a DEPRECATED warning. remove the unnecessary code please.
- any feature needs to be tested both with code and playwright.
- Any new feature that needs to be done needs to have acceptance criteria. You should ask for it, to get it if it is missing, or suggest one for approval.

## Environment & Server

- Server: 157.173.109.52 (`ssh server` via ~/.ssh/config alias)
- Domain: bauernfeind.travel (DNS via Cloudflare, proxied)
- Assume all test paths are relative to project root

### Production Structure

```
/var/www/bauernfeind.travel/
├── app/                 # Django project (cloned from git)
├── venv/                # virtualenv with Python 3.12
├── static/              # Collected static files
├── media/               # User uploads
├── logs/                # Gunicorn logs
└── gunicorn.sock        # Unix socket for Gunicorn
```

### Services

#### Gunicorn
- Service: `bftravel.service`
- Socket: `bftravel.socket`
- Start: `systemctl start bftravel`
- Status: `systemctl status bftravel`
- Logs: `/var/www/bauernfeind.travel/logs/`

#### Nginx
- Config: `/etc/nginx/sites-available/bauernfeind.travel`
- Test: `nginx -t`
- Reload: `systemctl reload nginx`

### Cloudflare SSL

- DNS: A records pointing to 157.173.109.52 (proxied)
- SSL/TLS Mode: Full
- Cloudflare handles SSL certificates automatically

### Firewall (UFW)

- Status: Active
- Allowed ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)

## Django Commands & Best Practices

- Run migrations: `python manage.py migrate`
- Run all tests: `python manage.py test`
- whenever you install something with pip install, always run freeze to requirements.txt
- by default, when someone needs interfaces to edit stuff, let's stay away from django admin. we will be building our own UI for editing things.

### Django Admin

- URL: https://bauernfeind.travel/admin/
- Email: ilina96@gmail.com
- Password: admin123 (change this after first login)

## Database & Migrations

- NEVER write your own migrations!
- do not use -fake flag for migrations. if there is a problem report to me and let's discuss it
- Do not ever touch migrations manually unless explicitly asked. always use Django to create migrations. or make further modifications of a model through a new migration rather than editing an old migration.
- When creating migrations, always think of how those migrations will work when migrating on production. Changing, removing fields, should not cause hiccups. The migrations on production should go through seamlessly without any interventions
- modifying database manually on local development or production is unacceptable. never do it.

## Production Data Compatibility

- **This project is live in production with real user data.** All new features, bug fixes, and refactors MUST be backward-compatible with existing production data.
- Never assume fields are populated — older records may have empty/null values for fields added later. Always handle missing or default data gracefully.
- New code must work correctly with data created before the feature existed.
- When adding new required fields to models, always provide a sensible default or make them nullable to avoid breaking existing rows.
- Test your changes against scenarios with "old-style" data, not just freshly created records.
- If a feature changes how data is stored or structured, ensure the old format is still readable and functional without requiring a manual data migration.

## Code Style

- **Do NOT use Django signals** for business logic. Signals make code hard to trace and debug. Call functions explicitly instead.
- Follow PEP 8 Python style guide
- Use snake_case for variables and functions
- **Do NOT include ticket/issue keys in code comments**. Keep comments clean and descriptive without referencing branch names or issue keys.
- Use PascalCase for classes
- Group imports: standard library, Django, third-party, local apps
- When importing, always put the imports at the top of the file, not within the functions and methods.
- reorganize the imports according to PEP 8 standards - grouping them logically and ordering them alphabetically within each group.
- Include type hints for function parameters and returns
- Use try/except blocks with specific exception types
- Test files should be prefixed with `test_`
- Models should have docstrings explaining their purpose
- Use Django's built-in ORM methods over raw SQL when possible
- if you need a logger, define one at the top and reuse it through the entire file.

## Python Conventions

- **Use `config()` from python-decouple, not `os.environ`** for reading environment variables.
- **Always read env vars at runtime** (inside methods/functions), never at class level or import time.

## UI/Frontend Conventions

- **Confirm exact page path before UI changes.** Always verify the exact route before placing UI elements. Ask if unsure.

## UI/UX Development Process

### Two workflows exist for UI work. Always determine which one applies before writing code.

#### Workflow 1: Mockup-First (New Features / New Pages)
Use when building new pages or significantly redesigning existing ones.

1. Create mockups under a dedicated dev-only route (e.g., `/dev/mockups/<name>/`)
2. Mockups MUST inherit the app's base template, CSS, and navigation — never build in isolation
3. Use hardcoded fake data that represents realistic scenarios (include edge cases: empty states, long text, many items, error states)
4. Iterate on the mockup until the user approves
5. Only then wire it into real views, models, and URLs
6. Delete the mockup route after migration

Rules for mockups:
- Keep them in a single template file when possible
- Include comments marking which data will come from which model/API
- Test at least 3 states: happy path, empty/zero state, error/loading state
- Respect existing UI patterns (see UI Component Patterns below)

#### Workflow 2: UI Audit & Optimization (Existing Pages)
Use when the user asks to improve, reorganize, simplify, or consolidate existing UI.

Before changing anything, produce a structured audit document:

1. Scan all templates and views in the project
2. For each page/screen, document:
   - URL pattern and view name
   - Purpose (one sentence)
   - Data displayed (models/fields)
   - Actions available (forms, buttons, links)
   - Navigation: what links HERE, what does this link TO
   - Shared data: which other pages show the same information
3. Output as a structured markdown document at `docs/ui-audit.md`
4. STOP and present the audit to the user — do not make changes yet
5. Discuss consolidation opportunities with the user
6. Only implement changes after explicit approval of the restructuring plan

#### UI Component Patterns
When this section is populated, always use these patterns for consistency.
If this section is empty, extract patterns from the existing codebase before creating new UI.

#### General UI Rules
- Never create a new visual pattern when an existing one fits
- When adding a page, first check if the content belongs on an existing page as a section or tab
- Every page must have a clear single purpose — if you can't state it in one sentence, it should probably be split or merged
- Prefer fewer pages with tabs/sections over many shallow pages
- Navigation depth should rarely exceed 2 levels from the main nav
- Always include: empty states, loading states, error states
- Mobile responsiveness is required unless explicitly told otherwise

## UI/CSS Development Guidelines

### Technology Stack (MANDATORY)

- **Styling**: Tailwind CSS only - no custom CSS, no Bootstrap.
- **Interactivity**: Alpine.js for all JavaScript interactions
- **Components**: Build custom components with Alpine.js + Tailwind
- **No other frameworks**: Avoid jQuery, Bootstrap, custom JS libraries

### Implementation Rules

1. All styling via Tailwind utility classes
2. All interactions via Alpine.js directives (x-data, x-show, x-on, etc.)
3. Use Alpine.js for: dropdowns, modals, form interactions, toggles
4. Follow Tailwind responsive patterns (sm:, md:, lg:, xl:)
5. Never write custom CSS or inline JavaScript

### Alpine.js Live Updates (No Page Refresh)

When a component needs to update reactively from external code (other JS files, iframes, API responses):

**Pattern that works:**
1. Add a unique `id` to the Alpine component element: `<div id="my-component" x-data="...">`
2. Create an update method inside the component's `x-data`:
   ```javascript
   x-data="{
       items: [],
       addItem(newItem) {
           this.items.unshift(newItem);  // Alpine reactivity triggers automatically
       }
   }"
   ```
3. Call from external JS using `Alpine.$data()`:
   ```javascript
   const el = document.getElementById('my-component');
   if (el && window.Alpine) {
       const data = Alpine.$data(el);
       data.addItem({ id: 123, name: 'New Item' });
   }
   ```

**What does NOT work reliably:**
- Custom window events (`window.dispatchEvent` + `@custom-event.window`) - often fails silently
- Adding update code in the wrong file (put notification where action originates, not where data lives)

**Key insight:** Always trace where the action originates (button click, API call) and add the notification code there, not in the component that displays the data.

### CSS Writing Rules

- No inline styles in templates (rare exceptions must be justified)
- All custom CSS goes in dedicated CSS files, not in `<style>` tags
- Use existing CSS classes from previous features when possible
- Document any new CSS classes added

## Template Guidelines

- in general, when building templates, do not put conditionals around variables to be displayed. we always want to display a variable, the conditional should only be around the value: either display it if it exists or let's say displaying '-' if no value.
- when i ask you to make tooltips please use tippy.js implement it once in the header of the base.html and let's be done.

## Git & Deployment

- Don't commit automatically to git. i will be letting you know if you need to commit on a per-feature base. so even if i told you in the past to commit to a feature, do not commit next feature unless you are told so specifically.
- Only commit after testing. Never commit untested code.
- Don't ever deploy to production, login to git pull, or modify files or scp there without my explicit ask

### Deployment

**ALWAYS use the deploy script. NEVER run deployment steps manually or separately.**

```bash
./deploy.sh
```

The script handles everything:
1. Warns about uncommitted changes
2. Pushes to main branch
3. Creates a deployment tag (e.g., `production-2026-03-15-1`)
4. SSHs to server and runs: git pull, pip install, collectstatic, migrate, restart services

Do NOT manually SSH to run individual deployment commands. Use the script.

## Branch & Commit Conventions

- **Before starting work**: Always sync develop with remote develop to pull latest changes: `git checkout develop && git pull origin develop`
- **Branch naming**: Create branches with format: `YYMMDD-summary-name` (date-based)
  - Example: `260202-feature-name`
  - If user specifies a different name explicitly, use that instead
- **Commit messages**: Short and precise descriptions
  - Example: `Fix waiting list approval`
  - Keep messages short and precise (avoid long explanations in the first line)

## Testing

- **NEVER run the full test suite** unless the user specifically asks for it. Run only targeted tests relevant to the changes made.
- This project has pre-commit hooks that run tests. Expect test output before commits succeed.

## Specifications

All specs go in project root `specs/` folder.

## Browser Testing with Playwright

Use Playwright MCP tools for browser testing. Screenshots go to `browser-testing/artifacts/`.

## Reusable Systems Documentation

**IMPORTANT**: When building any reusable system, component, or utility that could be used across the codebase, add a brief description here so Claude Code knows it exists for future tasks. Include enough detail to understand what it does and which files to examine.
