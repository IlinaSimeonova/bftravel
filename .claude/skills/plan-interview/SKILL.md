---
name: plan-interview
description: |
  Interview-based planning using provided spec/plan files.
  Forces structured questions via AskUserQuestion to refine requirements.
  Usage: /plan-interview path/to/file1.md path/to/file2.md
---

# Plan Interview Skill

## Purpose

Conduct an interactive interview based on provided plan/spec files to:
- Clarify ambiguous requirements
- Identify missing acceptance criteria
- Validate technical approach
- Surface edge cases and risks

## MANDATORY RULES

1. **MUST use AskUserQuestion tool** for every question - no plain text questions
2. **Read ALL provided files first** before asking questions
3. **Ask focused questions** - max 4 questions per round
4. **Track answered questions** - don't repeat

## Workflow

### Step 1: Read Files

Read all files passed as arguments. If no files provided, ask user to specify.

### Step 2: Analyze & Identify Gaps

Review the files for:
- Missing acceptance criteria
- Unclear requirements
- Unspecified edge cases
- Technical decisions needed
- Integration points unclear
- Testing strategy gaps

### Step 3: Interview Rounds

For each gap identified, use AskUserQuestion with:
- Clear, specific question
- 2-4 predefined options where applicable
- Allow "Other" for custom input

**Question Categories to Cover:**

1. **Scope Clarification**
   - What's in/out of scope?
   - MVP vs future phases?

2. **User Experience**
   - Who are the users?
   - What's the expected flow?
   - Error handling approach?

3. **Technical Decisions**
   - Technology choices?
   - Integration patterns?
   - Data model questions?

4. **Edge Cases**
   - What happens when X fails?
   - Boundary conditions?
   - Concurrent access?

5. **Testing & Verification**
   - How will we verify this works?
   - What are the acceptance tests?

### Step 4: Create Implementation Spec File

After interview complete, **ALWAYS** create a new implementation spec file:

1. **Determine the next spec number:**
   - Look at the input file path (e.g., `specs/68-feature/68-01-research.md`)
   - Extract the spec number prefix (e.g., `68`)
   - Find the highest existing file number in that folder (e.g., `01`)
   - Increment it (e.g., `02`)
   - New filename: `{spec-number}-{next-number}-implementation-spec.md`
   - Example: `68-01-research.md` → create `68-02-implementation-spec.md`

2. **Create the implementation spec file with this structure:**

```markdown
# [Feature Name] - Implementation Spec

**Spec:** [spec-number]-[feature-name]
**Date:** [current date]
**Status:** Ready for Implementation

---

## 1. Overview
[Brief description of the feature and its purpose]

## 2. Requirements Summary

### 2.1 Interview Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
[All Q&A decisions in table format]

### 2.2 What Gets Duplicated/Created/Modified
[Clear breakdown of what the feature does]

## 3. Technical Design
[Architecture diagram/description, service design, key patterns]

## 4. Data Model Analysis
[Fields to copy/create/modify, relationships, remapping logic]

## 5. Implementation Plan

### 5.1 Files to Create/Modify
| File | Action | Purpose |
|------|--------|---------|
[List all files]

### 5.2 Implementation Steps
[Numbered steps to implement]

## 6. API Specification
[Endpoints, request/response formats]

## 7. UI Specification
[Button placement, UX flow, components]

## 8. Testing Strategy
[Test cases, manual testing checklist]

## 9. Acceptance Criteria
[Checkboxes for all requirements]

## References
[Links to related specs/files]
```

3. **Tell the user in chat:**
   > Created implementation spec: `specs/XX-feature/XX-YY-implementation-spec.md`
   >
   > This file contains all decisions and complete implementation details.
   > You can give this file to a new Claude session to implement the feature.

## Example Usage

```
/plan-interview specs/65-new-feature/65-01-specs.md

/plan-interview specs/65-new-feature/65-01-specs.md specs/65-new-feature/notes.md
```

## Question Format Examples

```
AskUserQuestion:
  question: "How should the system handle duplicate entries?"
  header: "Duplicates"
  options:
    - label: "Reject with error"
      description: "Show error message, don't create"
    - label: "Auto-merge"
      description: "Combine data from both entries"
    - label: "Create anyway"
      description: "Allow duplicates in the system"
```

## Output

After interview, **ALWAYS**:
1. Create the new implementation spec file (incremented number)
2. Tell user the file path in chat
3. Confirm the file contains everything needed for implementation
