# Origin Apps

Plugin for teams bringing an existing GitHub App to
[Cursor Origin](https://cursor.com/docs/api/origin), Cursor's code forge.
Skills only, so it runs in Cursor, Claude Code, Codex, and any agent that
reads [Agent Skills](https://agentskills.io).

## What it includes

- `port-github-app-to-origin`: run it inside your GitHub App's repository with
  no other instructions. It discovers the app's GitHub surface from the code
  (manifest, permissions, events handled, payload fields read, REST and GraphQL
  calls, token minting, webhook receiver, calls your framework makes for you),
  fetches the live Origin API spec, and writes a porting brief: a capability
  table, the webhook fields your handlers read and where each comes from on
  Origin, the scopes to request, a hello-world path to your first real event,
  gaps worth raising with Cursor, and the questions your team should settle
  first.

The skill plans; it does not write port code, pick a language or SDK, or
estimate in time. Mappings come from the Origin OpenAPI spec at run time, so the
brief tracks the API as published on the day you run it.

## When to use

- You have a GitHub App (Probot, Octokit, go-github, hand-rolled) and want to
  know what an Origin App version looks like before you start.
- You are an agent working on such a team's behalf and need a grounded plan.
- You want to check which GitHub features Origin deliberately does not
  reproduce, and what the Origin idiom is instead.

In Cursor, open the app's repository and ask to port it to Origin, or run
`/port-github-app-to-origin`.

## Install in Cursor

Search for **Origin Apps** in the Cursor Marketplace
([cursor.com/marketplace/origin-apps](https://cursor.com/marketplace/origin-apps)),
or open **Customize**, find the plugin, and install it at user or project
scope.

## Use outside Cursor

The plugin ships three manifests for one set of skills: a root `plugin.json`
([Agent Plugins](https://agent-plugins.org) 1.0), `.cursor-plugin/plugin.json`
(Cursor Marketplace), and `.claude-plugin/plugin.json` (Claude Code). The
skill uses only portable frontmatter (`name`, `description`, `license`,
`compatibility`).

**Claude Code**, via the marketplace manifest at this repository's root:

```text
/plugin marketplace add cursor/plugins
/plugin install origin-apps@cursor-plugins
```

**Any agent that reads Agent Skills** (Claude Code, Codex, and others): copy
the skill directory into the agent's skills folder.

```bash
git clone --depth 1 https://github.com/cursor/plugins.git
# Claude Code
mkdir -p .claude/skills && cp -r plugins/origin-apps/skills/port-github-app-to-origin .claude/skills/
# Codex
mkdir -p .codex/skills && cp -r plugins/origin-apps/skills/port-github-app-to-origin .codex/skills/
# Cursor, without the marketplace
mkdir -p .cursor/skills && cp -r plugins/origin-apps/skills/port-github-app-to-origin .cursor/skills/
```

## Requirements

- Network access to `https://cursor.com/docs/api/origin/*` during the run.
- Read access to the app's source. No Origin credentials are needed to produce
  the brief; the hello-world path in the brief is what you follow afterwards.
- Optional: `python3` with PyYAML for `scripts/index-origin-spec.py`, which
  turns the fetched spec into a grep-friendly index. Without it the skill
  reads the spec directly.

## Where the brief goes

The skill writes `ORIGIN-PORTING-BRIEF.md` at the repository root and prints
its path. Gap cards in the brief are yours to send: through your shared Slack
channel with Cursor if you have one, or to `hi@cursor.com`.

## License

MIT
