# UI Execute

Execute the reorganization plan from `docs/ui-plan.md`.

## Prerequisites

- `docs/ui-plan.md` must exist. If not, tell the user to run /ui-plan first.
- If mockups were created during this process, check `/dev/mockups/` for approved designs to use as visual reference.

## How It Works

1. Read `docs/ui-plan.md` in full
2. Read `docs/ui-audit.md` for additional context on current state
3. Find the **Migration Sequence** section in the plan
4. Execute steps ONE AT A TIME in order
5. After completing each step:
   - State what was changed (files created, modified, deleted)
   - Confirm the app still works (run any relevant tests, check for import errors)
   - **STOP and wait for the user's approval before proceeding to the next step**
6. If a step fails or something unexpected comes up, explain the issue and wait for guidance

## Rules

- Follow the plan's migration sequence exactly. Do not skip steps or reorder them.
- Each step must leave the app in a working, deployable state.
- If the plan references mockup templates in `/dev/mockups/`, use their HTML/layout as the basis for the real implementation.
- When moving template content between files, preserve all Alpine.js interactivity, Tailwind classes, and data loading patterns.
- When a step says "extract shared utility", create it in a sensible location and update ALL callers — don't leave any duplicated code behind.
- When removing pages, always add redirects from old URLs to new ones before deleting.
- Do not modify any pages or functionality that the plan explicitly says "does not change."

## Resuming

If arguments are provided, they indicate which step to resume from:
$ARGUMENTS

For example: `/ui-execute Step 3` will skip to Step 3 assuming earlier steps are done.

If no arguments, start from Step 1 (or the first incomplete step if some are already done — check the codebase state).
