# Origin Apps

Plugin for building on [Cursor Origin](https://cursor.com/docs/api/origin),
Cursor's code forge: creating an Origin App, calling the API, receiving
webhooks, or bringing an existing GitHub App across. Skills only, so it runs
in Cursor, Claude Code, Codex, and any agent that reads
[Agent Skills](https://agentskills.io).

## What it includes

- `origin-api`: the general skill. Points the agent at the live docs and
  OpenAPI spec first (the only source for endpoints, scopes, and event slugs),
  then carries the practices that hold across spec versions: app, installation,
  and user credentials and just-in-time token minting; minimal scopes derived
  from `x-origin-scopes`; webhook subscription, `v1ed` signature verification,
  idempotent handling, and delivery behavior; opaque page tokens; TypeIDs; the
  error envelope; rate limits; and the deliberate differences from GitHub (no
  commit statuses, Issues, or GraphQL). Use it for any Origin work.
- `port-github-app-to-origin`: builds on `origin-api` for one job. Run it
  inside your GitHub App's repository with no other instructions. It discovers
  the app's GitHub surface from the code (manifest, permissions, events
  handled, payload fields read, REST and GraphQL calls, token minting, webhook
  receiver, calls your framework makes for you), maps it onto the live spec,
  and writes a porting brief: a capability table, the webhook fields your
  handlers read and where each comes from on Origin, the scopes to request, a
  hello-world path to your first real event, gaps worth raising with Cursor,
  and the questions your team should settle first. It plans; it does not write
  port code, pick a language or SDK, or estimate in time.

Both skills fetch the spec at run time and refuse to name an endpoint from
memory, so their output tracks the API as published on the day you run them.

## When to use

- You are writing or reviewing code that calls Origin, mints installation
  tokens, or receives Origin webhooks: `origin-api`.
- You are creating an Origin App and want the hello-world path and the
  first-week traps up front: `origin-api`.
- You have a GitHub App (Probot, Octokit, go-github, hand-rolled) and want to
  know what an Origin App version looks like before you start:
  `port-github-app-to-origin`.
- You want to check which GitHub features Origin deliberately does not
  reproduce, and what the Origin idiom is instead: either.

In Cursor, ask about the Origin API or ask to port the app; or run
`/origin-api` or `/port-github-app-to-origin`.

## Install in Cursor

Search for **Origin Apps** in the Cursor Marketplace
([cursor.com/marketplace/origin-apps](https://cursor.com/marketplace/origin-apps)),
or open **Customize**, find the plugin, and install it at user or project
scope.

## Use outside Cursor

The plugin ships three manifests for one set of skills: a root `plugin.json`
([Agent Plugins](https://agent-plugins.org) 1.0), `.cursor-plugin/plugin.json`
(Cursor Marketplace), and `.claude-plugin/plugin.json` (Claude Code). The
skills use only portable frontmatter (`name`, `description`, `license`,
`compatibility`).

**Claude Code**, via the marketplace manifest at this repository's root:

```text
/plugin marketplace add cursor/plugins
/plugin install origin-apps@cursor-plugins
```

**Any agent that reads Agent Skills** (Claude Code, Codex, and others): copy
the skill directories into the agent's skills folder. Copy both; the porting
skill refers to `origin-api` for fundamentals.

```bash
git clone --depth 1 https://github.com/cursor/plugins.git
# Claude Code
mkdir -p .claude/skills && cp -r plugins/origin-apps/skills/* .claude/skills/
# Codex
mkdir -p .codex/skills && cp -r plugins/origin-apps/skills/* .codex/skills/
# Cursor, without the marketplace
mkdir -p .cursor/skills && cp -r plugins/origin-apps/skills/* .cursor/skills/
```

## Requirements

- Network access to `https://cursor.com/docs/api/origin/*` during the run.
- For the porting skill: read access to the app's source. No Origin
  credentials are needed to produce the brief; the hello-world path in the
  brief is what you follow afterwards.
- Optional: `python3` with PyYAML for the porting skill's
  `scripts/index-origin-spec.py`, which turns the fetched spec into a
  grep-friendly index. Without it the skill reads the spec directly.

## Where the brief goes

The porting skill writes `ORIGIN-PORTING-BRIEF.md` at the repository root and
prints its path. Gap cards in the brief are yours to send: through your shared
Slack channel with Cursor if you have one, or to `hi@cursor.com`.

## License

MIT
