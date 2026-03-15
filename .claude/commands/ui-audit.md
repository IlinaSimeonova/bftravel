# UI Audit

Perform a structural audit of the application's UI. Do NOT make any changes — only analyze and report.

## Scope

If URLs or page names are provided as arguments, audit ONLY those pages and their immediate neighbors (pages that link to/from them). This keeps the audit focused and efficient.

If no arguments are provided, audit the entire application.

## Steps

1. Find URL patterns (urls.py files) — only the in-scope routes if scoped
2. Find templates and map them to their views — only in-scope ones
3. For each page/screen, document in a structured table:
   - **Route**: URL pattern
   - **View**: View class/function name
   - **Purpose**: One-sentence description of what the user does here
   - **Data shown**: Which models and fields are rendered on this page
   - **Actions**: Forms, buttons, and their effects (what POST/PATCH/DELETE endpoints they hit)
   - **Inbound links**: Which other pages link to this page
   - **Outbound links**: Which pages does this link to
   - **Shared data**: Flag any data that also appears on other pages (duplication)

4. After the per-page audit, add an analysis section:
   - **Navigation map**: A simple text diagram showing how pages connect
   - **Data duplication**: List every piece of data that appears on more than one page
   - **Orphan pages**: Pages with no inbound links (unreachable from nav)
   - **Deep pages**: Pages that require 3+ clicks from the main entry point
   - **Action overlap**: Different pages that can perform the same action
   - **Candidates for merging**: Pages that serve very similar purposes or share most of their data
   - **Candidates for splitting**: Pages that serve multiple unrelated purposes

5. Extract current UI patterns and list them:
   - What CSS framework/component library is used
   - Common layout patterns (sidebar, cards, tables, modals, tabs)
   - Form patterns (inline, full-page, modal)
   - How empty states are handled (or if they're missing)
   - How errors/loading are handled

6. Save the complete audit to `docs/ui-audit.md`

7. Present a summary to me and STOP. Do not suggest or make any changes. I will review the audit and decide what to do next.

$ARGUMENTS
