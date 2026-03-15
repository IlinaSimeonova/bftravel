# Specifications & Status Reports

All specs go in this `specs/` folder.

## Naming Convention

- **Folders:** `XX-feature-name/` (two-digit sequence, lowercase hyphenated)
- **Files:** `XX-YY-description.md` (XX = folder number, YY = file sequence)
- Sequence numbers are unique per repository

## Structure

```
specs/
├── 01-feature-name/
│   ├── 01-01-requirements.md
│   └── 01-02-implementation.md
├── 02-another-feature/
└── ...
```

## When to Create Specs

- New features or major changes
- Architecture decisions (ADRs)
- Implementation status reports
- Troubleshooting guides
- Security audits and compliance
- API design docs
- Post-incident reviews

## Spec File Template

```markdown
# [Feature/Topic Name]

## Context
Why this exists, what problem it solves.

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2

## Design / Approach
How it will be implemented.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Status
- [ ] In progress / Complete / Blocked
```
