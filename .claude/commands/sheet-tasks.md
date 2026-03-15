---
name: sheet-tasks
description: Fetch tasks from Google Sheet and prepare task file for development
args: "<SheetTabName> - the name of the sheet tab to fetch tasks from (e.g., '02-06.03')"
---

# Sheet Tasks Fetcher

You are fetching tasks from the BigBongo task tracking Google Sheet and preparing them for development.

## Instructions

1. **Fetch tasks**: Use `mcp__google-sheets__get_tasks` with sheet_name set to `$ARGUMENTS` and status filter `"In Progress"` to get all tasks ready for development.

2. **Create task file**: Write a markdown file at `google-sheets-mcp/tasks/YYYYMMDD-tasks.md` (using today's date, e.g., `20260302-tasks.md`). The file should contain:

```markdown
# Tasks from [SheetTabName] - YYYY-MM-DD

## Summary
- **Sheet**: [tab name]
- **Total tasks**: [count]
- **Date fetched**: YYYY-MM-DD

## Tasks

### [ID] - [Task Title]
- **Group**: [group]
- **Priority**: [priority]
- **Status**: [status]
- **Description**: [full description from sheet]
- **Implementation status**: Pending

---
(repeat for each task)
```

3. **Review and clarify**: After creating the file, review ALL task descriptions carefully:
   - If any task description is **vague, ambiguous, or missing key details**, list the specific questions and ask the user using AskUserQuestion
   - If any task seems to **conflict with another task**, flag it
   - If any task requires **architectural decisions**, flag it
   - Group your questions by task ID for clarity

4. **DO NOT start implementing**. Your job here is ONLY to:
   - Fetch and document the tasks
   - Ask clarifying questions if needed
   - Wait for the user to give the green light to start development

5. **Output**: After creating the file and asking questions (if any), summarize:
   - How many tasks were fetched
   - How many need clarification
   - Which tasks are clear and ready to go
