# Claude-Pilot

Auto-generated codebase orientation for Claude Code. Generates an LLM-optimized map so CC starts every session knowing the project instead of groping around for 5-10 minutes.

## Usage

```bash
# From project root:
python3 .claude-pilot/cli.py init          # Generate map, install hooks, wire up CLAUDE.md + MCP
python3 .claude-pilot/cli.py refresh       # Full map regeneration
python3 .claude-pilot/cli.py refresh --quick  # Activity section only (<0.1s)
python3 .claude-pilot/cli.py status        # Map age, hook status, index stats
python3 .claude-pilot/cli.py uninstall     # Remove everything (hooks, generated files, CLAUDE.md ref, MCP)
```

## What `init` does

1. Generates `.claude-pilot/map.md` — compact project briefing (~1K tokens)
2. Builds `.claude-pilot/index.json` — file/symbol index for the Navigator
3. Installs git hooks — post-commit (quick refresh), post-checkout/post-merge (full refresh)
4. Adds `@.claude-pilot/map.md` to CLAUDE.md so CC reads the map on every session
5. Registers the Navigator MCP server in `.mcp.json`
6. Adds `.claude-pilot/index.json` to `.gitignore`

## Three Components

**Map** — Single markdown file with 5 layers: identity (framework, DB, services), structure (annotated directory tree), relationships (imports, URL routes, model FKs), activity (branch, hot files, recent commits), conventions (tests, linters, patterns).

**Navigator** — MCP server with 5 tools for depth-on-demand after orientation:
- `get_module_context(path)` — briefing on a file/directory
- `get_recent_changes(scope, days)` — structured git history
- `get_dependencies(file)` — import graph both directions
- `get_patterns(type)` — code examples by pattern type (view, model, form, etc.)
- `search_context(query)` — keyword search with context

**Updater** — Git hooks keep the map fresh automatically. Post-commit updates activity (<0.1s). Branch switches and merges trigger full rebuilds.

## Framework Detection

Detects and deeply analyzes: **Django** (AST-based settings/models/URLs parsing), **Flask/FastAPI**, **Node.js/Express/Next.js** (package.json), with a universal fallback for anything else.

## Zero Dependencies

Map generation and updater use only Python stdlib. The Navigator MCP server requires `mcp` (auto-installed during init if missing).

## Portability

This folder is self-contained. Drop it into any git project and run `python3 .claude-pilot/cli.py init`.
