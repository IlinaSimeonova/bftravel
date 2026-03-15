---
name: chrome-test-flow
description: Test a specific user flow in Chrome with step-by-step verification
---

Interactively test a specific user flow with verification at each step.

Usage: `/chrome-test-flow <description of flow to test>`

Examples:
- `/chrome-test-flow login with valid credentials`
- `/chrome-test-flow create new workflow and verify it saves`
- `/chrome-test-flow submit contact form with invalid email`

## Steps

1. **Understand the flow**
   - Parse user's description
   - Identify: starting point, actions, expected outcomes

2. **Setup browser**
   - `tabs_context_mcp` with `createIfEmpty: true`
   - `update_plan` with domains and test approach

3. **Execute flow with verification**
   For each step:
   - Take screenshot BEFORE action
   - Perform action
   - Take screenshot AFTER action
   - Verify expected state
   - Check console for errors
   - Report step result (✅/❌)

4. **Final verification**
   - Check console for any errors
   - Check network for failed requests
   - Take final screenshot

5. **Report results**
   - Step-by-step breakdown
   - Overall PASS/FAIL
   - Any issues found

## Output Format

```
## Flow Test: [Description]

### Test Steps

| Step | Action | Expected | Actual | Status |
|------|--------|----------|--------|--------|
| 1 | Navigate to /login | Page loads | Page loaded | ✅ |
| 2 | Enter email | Field populated | Field filled | ✅ |
| 3 | Click submit | Form submits | Error shown | ❌ |

### Console Errors
[Any JS errors]

### Network Issues
[Any failed API calls]

### Screenshots
[Key screenshots from the flow]

### Result: ✅ PASS / ❌ FAIL
[Summary of test outcome]
```

## Common Test Patterns

### Login Flow
```
1. Navigate to /accounts/login/
2. Find email field → fill
3. Find password field → fill
4. Click sign in
5. Verify redirect to dashboard
```

### Form Submission
```
1. Navigate to form page
2. Fill all required fields
3. Click submit
4. Verify success message OR error handling
```

### CRUD Operation
```
1. Navigate to list page
2. Click create button
3. Fill form
4. Submit
5. Verify item in list
6. Click edit
7. Modify field
8. Save
9. Verify changes
10. Delete item
11. Verify removal
```

## Verification Methods

- **Visual**: Screenshot comparison
- **Text**: Check for expected text on page
- **Console**: No JS errors
- **Network**: API calls succeed (200/201)
- **State**: Alpine.js component data is correct

## Token Cost
~5000-12000 tokens depending on flow complexity
