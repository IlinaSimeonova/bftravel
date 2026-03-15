---
name: feature-planning
description: |
  Use when starting new features, epics, or significant implementations.
  Creates structured specs in the correct location with proper breakdown.
  Auto-triggers on: "new feature", "implement", "add functionality", "build", "create".
---

# Feature Planning Workflow

## When to Use This

Use this skill when:
- Starting a new feature (not a bug fix)
- Implementing something that requires design decisions
- Working on a task that spans multiple files/components
- Beginning work on a Jira epic or story

## Spec Folder Structure

Location: `specs/{NN}-{feature-name}/`

Where:
- `NN` = Two-digit sequence number (check existing folders for next number)
- `feature-name` = Short, descriptive name (lowercase, hyphenated)

### Required Files

```
specs/{NN}-{feature-name}/
├── {NN}-01-specs.md           # Initial analysis & specification
├── {NN}-02-implementation.md  # Progress tracking (created during dev)
└── {NN}-03-completion.md      # Final report (created when done)
```

## Workflow

### Phase 1: Planning (This Session)

1. **Create spec folder** with correct sequence number
2. **Write `{NN}-01-specs.md`** using the template below
3. **Break down into tasks** that can be implemented independently
4. **Identify risks** and decision points
5. **Save and exit** - planning session complete

### Phase 2: Implementation (New Session)

1. Open new Claude Code session
2. Reference: "Implement specs/{NN}-{feature-name}/"
3. Claude reads the specs and implements
4. Create `{NN}-02-implementation.md` with progress notes
5. Use `verification-before-done` skill before claiming complete

### Phase 3: Completion

1. Run full verification (see testing-workflow skill)
2. Create `{NN}-03-completion.md` with results
3. Update Jira issue with implementation details

## Finding Next Sequence Number

```bash
# Check existing spec folders
ls specs/ | tail -5
```

Use the next number after the highest existing one.

## Key Principles

### Break Down Tasks Correctly

Good task breakdown:
- Each task can be completed in one CC session
- Each task can be independently tested
- Clear success criteria for each task

Bad task breakdown:
- "Implement the feature" (too vague)
- Tasks that depend on decisions not yet made
- Tasks without clear completion criteria

### Separate Planning from Implementation

- **Planning session**: Research, design, document
- **Implementation session**: Code, test, verify

This separation prevents context overload and ensures proper design before coding.
