# UI Reorganization Plan

Read the UI audit and propose a reorganized page structure. Do NOT make any changes — only propose.

## Prerequisites

An audit must exist at `docs/ui-audit.md` or `docs/ui-audit-*.md`. If not, tell the user to run /ui-audit first.

## Analysis Steps

Read the audit document, then analyze through these lenses:

### 1. Data Clustering
Group pages by the data they share. Pages that display overlapping models/fields are candidates for merging into a single page with tabs or sections.

### 2. Action Clustering  
Group pages by what the user can DO on them. If two pages let you perform actions on the same entity (e.g., view workflow vs edit workflow), consider whether they should be one page with view/edit modes.

### 3. User Journey Mapping
Identify the 3-5 core tasks a user performs. Trace each task through the current pages. Flag:
- Tasks that require visiting 3+ pages to complete
- Tasks that require backtracking
- Dead-end pages with no clear "next action"

### 4. Redundancy Elimination
For every piece of data or action that appears on multiple pages, decide: where is its PRIMARY home? Everywhere else should either link to that home or show a minimal summary.

### 5. Navigation Simplification
Propose a navigation tree that is at most 2 levels deep. Every page must be reachable in 2 clicks from the main nav.

### 6. Visual and UX Optimization
For each page in the proposed structure, go beyond structure and think about how it should look and feel:

- **Section naming**: Propose clear, user-facing names. Avoid model/developer names. Name things by what the user needs, not what the database stores.
- **Redundant labels and headings**: Flag headings that repeat what's already obvious from context (e.g., a "Profile" heading inside a Profile tab). Remove or simplify.
- **Layout grouping**: Within each page, group related information together. Cards that show related data should be adjacent. Actions that relate to the same thing should be near each other.
- **Tab naming**: If the page has tabs, propose short, clear tab labels. Avoid generic names like "Details" or "Info" when something more specific fits.
- **Prominence hierarchy**: What should the user see first? What's secondary? What should be collapsed or hidden by default? Propose what's prominent vs. tucked away.
- **Redundant data within a page**: Flag any data that appears twice on the same page. Decide where it lives and remove the duplicate.
- **Card/section consolidation**: If two cards or sections show closely related info, propose merging them into one.
- **Action placement**: Where do buttons and actions go? Group related actions. Don't scatter them across the page.
- **Empty real estate**: Flag areas where the layout wastes space or where content could be reorganized to use space better.

Include these recommendations in the per-page proposals in the output, not as a separate section.

## Output

Produce a structured plan at `docs/ui-plan.md` with these sections:

### Proposed Page Structure
For each page in the new structure:
- **Name and URL**
- **Purpose** (one sentence)
- **Contains** (what data and actions live here)
- **Merged from** (which current pages this replaces, if any)
- **New** (if this page doesn't exist today)
- **Removed** (current pages that are eliminated, with explanation of where their content went)

### Navigation Map
A simple text diagram of the proposed navigation hierarchy.

### Change Summary
A short list of the key changes:
- Pages merged: X and Y → Z
- Pages split: A → B + C  
- Pages removed: D (content moved to E)
- Pages added: F (new, because...)
- Navigation changes: moved X from top nav to sub-section of Y

### Migration Sequence
Ordered list of changes to implement, starting with the least disruptive. Each step should leave the app in a working state.

## Then STOP

Present the plan summary and wait for the user's feedback. The user may:
- Approve the plan as-is → proceed to implementation or mockups
- Modify specific parts → update the plan
- Reject and discuss → the plan becomes input for a chat conversation

## Scope

If specific pages or areas are provided as arguments, limit the plan to those pages and their immediate context. Otherwise, plan across the entire audited surface.

$ARGUMENTS