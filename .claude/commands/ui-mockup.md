# UI Mockup

Create a mockup page for a new feature or redesign. The mockup uses fake data and is NOT wired to real views/models.

## Setup (first time only)

If the mockup route doesn't exist yet:
1. Add a dev-only URL namespace: `path('dev/mockups/', include('mockups.urls'))` (or equivalent)
2. Ensure it only loads in DEBUG mode
3. Create the mockups app/directory if needed

## Steps

1. Before creating anything, gather context:
   - If `docs/ui-plan.md` exists, read it first. It contains the approved reorganization plan — the mockup should implement what the plan describes. Use the plan's proposed page structure, tab layout, merged content, and navigation changes as your primary spec.
   - If `docs/ui-audit.md` or any `docs/ui-audit-*.md` exists, read it too. Use it to understand the current page structure, navigation patterns, data model relationships, and where this new page fits in the existing architecture. The mockup should feel like it belongs in the existing app.
   - The base template that all pages extend
   - CSS framework and existing component patterns
   - Navigation structure
   - Any existing UI component patterns documented in CLAUDE.md

2. Create the mockup template that:
   - Extends the real base template (inherits nav, CSS, footer)
   - Uses hardcoded data that is realistic (real-looking names, counts, dates — not "Lorem ipsum")
   - Includes HTML comments marking where real data would come from: `<!-- FROM: WorkflowStep.objects.filter(workflow=workflow) -->`
   - Shows multiple states (add sections or toggles for: populated, empty, error, loading)

3. Create a simple view that renders the template with no dependencies

4. Register the URL at `/dev/mockups/<number>/`

5. Tell me the URL and what states are available, then STOP and wait for feedback

## Iteration

When I give feedback:
- Make changes to the mockup template only
- Do not start wiring to real data until I explicitly say "approve" or "wire it up"
- Each iteration should be immediately viewable at the same URL

## Promotion (when approved)

When I approve the mockup:
1. Create the real view with proper model queries
2. Move the template to the correct app directory
3. Wire up the real URL
4. Connect forms/actions to real endpoints
5. Delete the mockup URL and template
6. Verify the page works with real (or empty) data

## What to build

If arguments are provided, use them as the description:
$ARGUMENTS

If NO arguments are provided (empty), read `docs/ui-plan.md` and identify the next page that needs mockup work. Look for pages marked as merged, restructured, or new. If the plan has multiple candidates, pick the most impactful one (usually the largest merge) and proceed. State what you're building and why before starting.