# Specifications & Status Reports Convention

All specs go in **project root** `specs/` folder. (`recorder/specs/` is archived from Electron era.)

## Naming

- **Folders:** `XX-feature-name/` (two-digit sequence, lowercase hyphenated)
- **Files:** `XX-YY-description.md` (XX = folder number, YY = file sequence)
- Sequence numbers are unique per repository

## Example

```
specs/
├── 01-initial/
├── 05-async/
├── 12-screenshots-r2/
│   ├── 12-01-backend-implementation.md
│   ├── 12-02-setup-instructions.md
│   └── 12-03-troubleshooting.md
```

## When to Create Specs

New features, major changes, implementation status reports, troubleshooting guides, architecture decisions, API design docs.
