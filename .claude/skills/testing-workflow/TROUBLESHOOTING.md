# Test Troubleshooting Guide

Common issues and how to resolve them.

## Server Issues

### "Connection refused" / Server not responding

```bash
# Check if server is running
curl -s localhost:8006/ || echo "Server not responding"

# Check debug log
tail -50 _logs/debug.log

# Don't kill the server on port 8006 - it's the main dev server
```

### "500 Internal Server Error"

```bash
# Check the debug log for traceback
tail -100 _logs/debug.log

# Look for the actual Python error
grep -A 20 "Traceback" _logs/debug.log | tail -25
```

## Test Failures

### Playwright tests timing out

- Increase wait times
- Check if element selectors are correct
- Verify server is responding
- Try running with `--headed` to see what's happening

### API tests failing with 404

- Check URL path is correct (trailing slash matters!)
- Verify the endpoint exists in urls.py
- Check if authentication is required

### curl returns HTML but expected JSON

- Endpoint might be returning error page
- Check for login redirect
- Verify Content-Type header

## Console Errors

### "Alpine is not defined"

- Alpine.js not loaded
- Check base template includes Alpine
- Check for script loading order issues

### "Uncaught TypeError"

- JavaScript error - check the exact line
- Often indicates missing data or wrong element

### "Failed to fetch" / Network errors

- API endpoint not responding
- CORS issues (check browser console)
- Wrong URL

## Database Issues

### "Relation does not exist"

```bash
# Run migrations
PYENV_VERSION=bigbongo-3-12-0 python manage.py migrate
```

### "IntegrityError" / Constraint violation

- Missing required field
- Duplicate unique value
- Foreign key doesn't exist

## Worker Issues

### Jobs not processing

```bash
# Check worker status
docker-compose -f docker-compose.workers.yml -f docker-compose.workers.local.yml ps

# Check worker logs
docker-compose -f docker-compose.workers.yml -f docker-compose.workers.local.yml logs --tail=50
```

### Jobs failing silently

```bash
# Check SQS queue for dead letters
# Or check worker logs for error messages
```

## Quick Diagnostics

```bash
# Full system health check
curl -s localhost:8006/ > /dev/null && echo "Server: OK" || echo "Server: DOWN"
docker-compose -f docker-compose.workers.yml ps 2>/dev/null | grep -q "Up" && echo "Workers: OK" || echo "Workers: DOWN"
```
