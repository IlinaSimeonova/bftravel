---
name: restart-local
description: Start/restart local Django server and rebuild Docker workers (Windows)
---

Start or restart the local development environment on Windows:

## Step 1: PostgreSQL

Check if PostgreSQL is running by testing connection on port 5433. If not running, start it:

```bash
"C:/Program Files/PostgreSQL/16/bin/pg_ctl.exe" -D "C:/Program Files/PostgreSQL/16/data" -l logfile start
```

## Step 2: Run Migrations

Run database migrations before starting the server:

```bash
./venv/Scripts/python.exe manage.py migrate
```

## Step 3: Django Server

Check if Django is running on port 8006 using curl.

- If running: kill the process first, then restart
- If not running: start it

To check:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8006/
```

To start (run in background):

```bash
./venv/Scripts/python.exe manage.py runserver 8006
```

## Step 3: Workers

Always rebuild and restart workers (force-recreate ensures new code is picked up):

```bash
cd workers && docker-compose -f docker-compose.workers.yml -f docker-compose.workers.local.yml up -d --build --force-recreate
```

## Step 5: Verify

Confirm Django server responds with 200:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8006/
```

Report status for each component.
