---
name: port-github-app-to-origin
description: >-
  Plans the port of an existing GitHub App to a Cursor Origin App. Use when the
  task is to bring a GitHub App to Origin or compare what it uses against the
  Origin API. Reads the app's needs out of its code, maps them onto the live
  Origin spec, and writes a porting brief with feedback for Cursor. Planning
  only.
license: MIT
compatibility: >-
  Needs network access to https://cursor.com/docs/api/origin/* at run time.
---

# Port a GitHub App to an Origin App

Run inside the app's codebase. The output is a porting brief for the team plus
a Feedback for Cursor section they can send as is (`references/brief.md`).
This skill plans; it does not write or change code unless the user explicitly
asks after reading the brief. Follow the `origin-api` skill for the docs and
the rules to check first. Two rules on top:

1. **Discover, do not ask.** Read what the app uses out of the code. Anything
   you cannot find becomes an open question.
2. **Feedback describes use cases, not the team's code.** Team-facing parts of
   the brief may cite `file:line`. Feedback for Cursor names only what the
   app needs to do and what Origin lacks for it, in Origin terms, with no file
   paths, module names, framework internals, or repository names.

## What to discover

Record a `file:line` for each, and note what you looked for and did not find.

- Declared permissions and events (manifest or IaC, if checked in; otherwise
  derive from the calls).
- Webhook events handled, and every payload field each handler reads,
  including fields used only for logging.
- REST and GraphQL call families, with the parameters and filters passed, the
  response fields read, whether each runs per webhook or in a loop, and the
  pagination style in use.
- Authentication: JWT algorithm, how the installation is identified after
  install, token lifetime handling, any user sign-in and what it is for,
  whether the app clones or pushes git.
- Webhook receiver: signature scheme, whether the raw body is available at
  verification time, how deliveries are deduplicated.
- Calls a framework or helper library makes on the app's behalf (Probot's
  receiver, token cache, and config loader; Octokit `App`'s installation and
  repository listing; app-auth libraries). Read the dependency's docs and
  list these as rows marked "from `<dependency>`".

## How to map

Fetch `openapi.yaml` and `llms-full.txt` whole; a brief needs broad coverage.
`rg -B1 -A4 'x-origin-scopes:' openapi.yaml` lists every operation with its
scope block; `rg -A3 'x-origin-webhook-events:' openapi.yaml` lists every
event slug with its payload schema. Each endpoint and each payload family has
a docs section with its fields expanded to dotted paths.

- A name match is a candidate, not a result. Confirm by reading the
  operation's description, parameters, and response fields against what the
  code passes and reads. A missing parameter or field the code depends on is
  a workaround or a gap, not a match.
- GitHub's issue-flavored pull request calls (`/issues/{n}/comments`,
  `/issues/{n}/labels` on a pull request) live under the pull request
  endpoints. Used on real issues, see the crib in `references/brief.md`.
- GraphQL has no counterpart; decompose each document into REST calls and
  record the fan-out.
- Scopes are the union of `x-origin-scopes.scopes` over the operations you
  named, not a translation of the manifest.
- Each event and action pair maps to at most one slug in "Events"; the action
  is part of the slug. A pair with no slug is not an event on Origin.
- For each payload field the code reads, record whether it is present, comes
  from the envelope (`event.type` carries the action), needs a follow-up read
  (say which operation and how many calls per event), is derivable, or is
  absent. Payloads are snapshots; a field on the REST resource that the
  payload lacks is a follow-up read.
- A capability the docs do not mention is not available today and gets a
  question. A behavior the docs neither confirm nor deny gets a question plus
  a first-run step that observes it, not an assumption carried over from
  GitHub.

## Before finishing

Every Origin claim resolves in the fetched files. Every gap has a feedback
entry naming a tradeoff. The feedback contains nothing that reveals the
team's internals. The summary names the native-or-mirror question.
