# Quick Verification Checklist

Use this checklist before saying any task is complete.

## For API Changes

- [ ] Endpoint returns correct status code (200, 201, 204, etc.)
- [ ] Response JSON matches expected structure
- [ ] Error cases return proper error responses
- [ ] Database state is correct after operation
- [ ] No console errors in browser

## For Template/UI Changes

- [ ] Page loads without errors (HTTP 200)
- [ ] No JavaScript errors in console (check bottom of curl response)
- [ ] Interactive elements work (buttons, forms, etc.)
- [ ] Data displays correctly
- [ ] Works in both light and dark mode (if applicable)

## For Form Changes

- [ ] Form renders correctly
- [ ] Validation works (try invalid input)
- [ ] Submission creates/updates correct database record
- [ ] Success/error messages display properly
- [ ] Redirect after submission works

## For Bug Fixes

- [ ] Original bug is actually fixed (run exact reproduction steps)
- [ ] Similar scenarios don't have same bug
- [ ] No new bugs introduced
- [ ] Related functionality still works

## For Background Jobs/Workers

- [ ] Job queues correctly
- [ ] Job executes without errors
- [ ] Job result is correct
- [ ] Worker logs show expected output
- [ ] Error handling works (try failure case)

## Verification Commands Quick Reference

```bash
# Check any page
curl -s localhost:8006/<page> | tail -100

# Check API endpoint
curl -s localhost:8006/api/<endpoint>/ | python -m json.tool

# Check worker logs
docker-compose -f docker-compose.workers.yml logs --tail=50

# Run specific test
PYENV_VERSION=bigbongo-3-12-0 pytest <app>/tests/ -k "<test_name>" -v

# Full test suite for feature
/test-all

# Interactive browser check
/chrome/test-flow <description>
```
