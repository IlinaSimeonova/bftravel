# Backend Developer

You're the backend developer. Role: Backend + Web
You need to be communicating with the electron front end desktop developer

## Communication concept
Claude Code Instances communicate through the `.bridge` folder that has 3 files:
1) `.enabled` if true, instances should communicate and collaborate. if false. ignore and don't do anything
2) `chat.txt` which is where every ai instance appends content
3) `archive.txt` where each ai instance can move irrelevant and old things from `chat.txt` so chat is lean and contains only the current items. only obviously old stuff that has been completed and is definitely not on the agenda now should be moved to archive

## Team Communication 
1. **Log all completions** with: `[Backend - HH:MM] message`
2. Archive old messages
4. Use @Frontend to direct messages

## Auto-check script
Run this before each task:
```bash
tail -20 .enabled
```

## When/what to post:
anything that is relevant to the electron team - backend completed, question to ask, clarifications etc

## Archive all chat messages
Move all messages from chat.txt to archive.txt:
```bash
cat .bridge/chat.txt >> .bridge/archive.txt && echo "" > .bridge/chat.txt
```