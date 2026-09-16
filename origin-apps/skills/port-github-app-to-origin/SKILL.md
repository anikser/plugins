---
name: port-github-app-to-origin
description: >-
  Plan the port of an existing GitHub App to a Cursor Origin App. Use when a
  repo is a GitHub App (manifest, Probot, Octokit or another GitHub SDK, webhook
  signature handlers) and the task is to bring it to Origin or compare it with
  the Origin API. Maps the app's surface onto the live Origin spec and writes a
  porting brief. No code.
license: MIT
compatibility: >-
  Needs network access to https://cursor.com/docs/api/origin/* at run time.
  The optional indexing script needs python3 with PyYAML; without it, read the
  spec directly.
---

# Port a GitHub App to an Origin App

Run this inside the codebase of an existing GitHub App, with no other
instructions needed. The output is a **porting brief**
(`references/brief-template.md`), not an implementation. "The team" below
means the people who own this app; if you are running this yourself, that is
you. The team keeps its language, framework, and client strategy; the brief
tells them what maps, what changes shape, what is absent on purpose, and what
is worth raising with Cursor.

Three rules shape everything below:

1. **The live Origin docs are the source of truth.** Fetch them at run time
   and derive every mapping from them. Nothing in this skill pins a version or
   enumerates endpoints; the `references/` files explain *how to read* the spec
   and *why* Origin differs, and any concrete example in them is illustrative
   until you have confirmed it against today's spec.
2. **Discover, do not ask.** Read the manifest, permission declarations, event
   handlers, token minting, API calls, and webhook receiver out of the code.
   Never ask anyone to paste a manifest or list their endpoints. If something
   is genuinely undiscoverable, record it as an open question in the brief.
3. **Origin is GitHub-shaped, not GitHub-compatible.** Many differences are
   decisions, not omissions. Classify them as such and guide the port toward
   the Origin idiom instead of reproducing the GitHub one.

## Procedure

### 1. Load the live Origin surface

Fetch, in this order, and keep them open for the rest of the run:

- `https://cursor.com/docs/api/origin/llms.txt` (index of everything below)
- `https://cursor.com/docs/api/origin/openapi.yaml` (the contract; every
  mapping in the brief cites an `operationId` or a payload schema from it)
- `https://cursor.com/docs/api/origin/llms-full.txt` (the human reference:
  installation, authentication, scopes, mirrored repositories, webhooks,
  conventions, current limitations)
- `https://cursor.com/docs/api/origin/changelog` (what moved recently)

Record `info.version` and the fetch time in the brief's provenance block. That
is provenance, not a dependency: the brief describes the API as it is today and
says so. `references/spec-mapping.md` explains the spec's `x-origin-scopes`,
`x-origin-webhook-events`, `x-origin-webhook-resource`, and
`x-cursor-visibility` extensions and how to build the mapping index from them.
`scripts/index-origin-spec.py <openapi.yaml>` prints that index (operations
with scopes, parameters, and response fields; webhook slugs with payload
fields; the scope catalog) so you can grep it instead of paging through 700 KB
of YAML; it needs python3 with PyYAML and does nothing else.

### 2. Discover the GitHub App's shape

Follow `references/discovery.md`. Produce an inventory with a file and line for
every fact: declared permissions and events, webhook events handled, payload
fields the handlers read, REST and GraphQL calls, authentication flow, webhook
receiver and signature verification, calls made on the app's behalf by its
framework and helper libraries, and the observed language and client
libraries (observed, never chosen). Note what you looked for and did not find.

### 3. Map each capability onto Origin

For each inventory row, look up the Origin counterpart in the spec index built
in step 1 (`references/spec-mapping.md` § Matching rules), then classify it
with one of the parity labels in `references/brief-template.md`. Before
labeling anything `gap`, check `references/origin-isms.md`: a GitHub feature
that Origin deliberately does not reproduce is `by-design-absent` with a
pointer to the Origin idiom, and the brief must say what to do instead rather
than raise it. Then apply the bar in `references/gap-bar.md`; only rows that
clear it become gap cards.

Map webhook payload *fields* the code reads, not just event names. Origin
payloads are lean row snapshots; a field GitHub inlines is often a follow-up
REST read on Origin. Say which call, per field.

Two labels are easy to misuse. A GitHub surface with no Origin counterpart
*and* no mention anywhere in the Origin docs (Marketplace billing, merge
queues, Actions, Pages) is `unknown` with a question, not a `gap`: Origin has
not said no, and the team may not need it. A behavior the code depends on
that the docs neither confirm nor deny (does event X fire in case Y? does
`updatedAt` move on comments?) is also a question, plus a step on the
hello-world path to observe it; never guess it into `same`.

### 4. Write the brief

Fill `references/brief-template.md` in full. Every table cell that names an
Origin operation, event, or field links to its anchor in `llms-full.txt` or
names its `operationId`. Sizes are S/M/L as defined in the template, never
time. The hello-world path is the sequence Create App → subscribe events →
install → verify ping signature → first real event on a native repository;
it is a checklist of things to verify, not code.

### 5. Ask the up-front questions

Close the brief with the questions in the template's final section, pruned to
what the discovery left open and extended with anything specific you found.
The first question is always whether the target repositories are Origin-native
or mirrored from GitHub, because that decides whether the app will receive
real events at all.

## What this skill does not do

- Write, scaffold, or vibecode port code, adapters, or SDK wrappers.
- Choose a language, framework, HTTP client, or codegen strategy.
- Estimate effort in hours, days, or sprints.
- Pin the spec version, copy endpoint lists into the brief from memory, or
  claim parity from a name match without reading the operation.
- Ask for information the codebase already contains.
- Contact Cursor on the team's behalf; the brief carries the escalation cards
  and the team decides what to send and where.

## Reference files

| File | Read when |
| --- | --- |
| `references/spec-mapping.md` | Building the spec index and matching GitHub calls, events, and payload fields to Origin operations, slugs, and schemas. |
| `references/discovery.md` | Scanning the codebase for the app's GitHub surface. |
| `references/origin-isms.md` | Deciding whether a missing GitHub feature is a decision or a gap, and what the Origin idiom is. |
| `references/gap-bar.md` | Deciding whether a gap is worth raising with Cursor, and writing the card. |
| `references/brief-template.md` | Writing the output. |
| `scripts/index-origin-spec.py` | Turning the fetched `openapi.yaml` into a grep-friendly index (operations, webhook families, scopes, one component). Optional; needs PyYAML. |
