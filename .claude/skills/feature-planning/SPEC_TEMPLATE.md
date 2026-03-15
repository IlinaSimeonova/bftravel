# Spec Template: {NN}-01-specs.md

Copy this template when creating a new spec file.

---

```markdown
# {Feature Name}

**Status**: Planning
**Created**: {YYYY-MM-DD}
**Jira**: {ISSUE-KEY} (if applicable)
**Purpose**: {One-line description of what this feature does}

---

## Problem Statement

{Describe the problem this feature solves. Why do we need this?}

### Current Situation

{What exists today? What's wrong with it?}

### Goals

{What will be better after this is implemented?}

---

## Requirements

### Minimal (Must Have)

- [ ] {Requirement 1}
- [ ] {Requirement 2}
- [ ] {Requirement 3}

### Nice to Have

- [ ] {Optional feature 1}
- [ ] {Optional feature 2}

### Future Improvements (Out of Scope)

- {Feature for later}
- {Another future consideration}

---

## Technical Analysis

### Files to Modify

| File | Change |
|------|--------|
| `app/models.py` | Add new model |
| `app/views.py` | Add new view |
| `app/templates/...` | New template |

### Files to Create

| File | Purpose |
|------|---------|
| `app/services/new_service.py` | Business logic |

### Database Changes

{Describe any model changes, migrations needed}

### API Changes

{New endpoints, modified endpoints}

---

## Implementation Plan

### Task 1: {Task Name}

**Files**: `file1.py`, `file2.py`
**Description**: {What this task accomplishes}
**Success Criteria**: {How to verify it's complete}

### Task 2: {Task Name}

**Files**: `file3.py`
**Description**: {What this task accomplishes}
**Success Criteria**: {How to verify it's complete}

### Task 3: {Task Name}

...

---

## Testing Plan

| Test Type | What to Test | Method |
|-----------|--------------|--------|
| Unit | Service logic | pytest |
| API | New endpoints | @api-tester |
| UI | User flow | /chrome/test-flow |

---

## Risks & Considerations

| Risk | Impact | Mitigation |
|------|--------|------------|
| {Risk 1} | {High/Medium/Low} | {How to prevent/handle} |

---

## Open Questions

- [ ] {Question that needs answering before implementation}
- [ ] {Another question}

---

## References

- {Link to related docs}
- {Link to design mockup}
- {Link to Jira issue}
```
