---
name: port-github-app-to-origin
description: >-
  Plans the port of an existing GitHub App to a Cursor Origin App. Use when a
  repo is a GitHub App (manifest, Probot, Octokit or another GitHub SDK, webhook
  signature handlers) and the task is to bring it to Origin or compare it with
  the Origin API. Maps what the app uses from GitHub onto the live Origin spec
  and writes a porting brief. No code.
license: MIT
compatibility: >-
  Needs network access to https://cursor.com/docs/api/origin/* at run time.
---

# Port a GitHub App to an Origin App

Run inside the GitHub App's codebase. The output is a porting brief
(`references/brief-template.md`), not an implementation. It says what maps,
what changes shape, what is not available today, and what is worth raising
with Cursor.

The `origin-api` skill in this plugin covers which docs to fetch, credentials,
scopes, webhooks, paging, IDs, and errors. Follow it first. Nothing here repeats it. Two rules on top:

1. **Discover, do not ask.** Read permissions, events, handlers, calls, token
   minting, and the receiver out of the code. Never ask for a manifest or an
   endpoint list. Anything you cannot find becomes an open question.
2. **Check the documented path first.** Anything in
   `references/origin-isms.md` has a documented Origin path or a documented
   limitation. Use the row's label; `not-available` rows still go through
   the gap bar.

## Procedure

1. **Load the spec** (`origin-api`, "Fetch first"). A brief needs broad
   coverage, so fetch the full `openapi.yaml` and `llms-full.txt`; the
   narrow lookup order in `origin-api` is for later single questions. Record
   `info.version` and the fetch time for the brief's provenance. Build the
   mapping index per `references/spec-mapping.md`.
2. **Discover** per `references/discovery.md`. Record a file and line for
   every fact, including payload fields read only for logging and calls the
   framework makes on the app's behalf. Note what you looked for and did not
   find.
3. **Map** each inventory row (`references/spec-mapping.md`, "Matching") and
   label it with the parity labels in the brief template. Map the webhook
   payload fields the code reads, not only the event names. If a payload
   lacks a field the REST resource has, read the resource; see the per-field
   notes under `#event-payloads`. Name the call for each such field. Then:
   - Check `origin-isms.md` before writing `gap`. Check `gap-bar.md` before
     writing any feedback entry.
   - A GitHub feature the Origin docs do not mention is `unknown` with a
     question. The question is how the team tells Cursor they need it.
   - A behavior the code depends on that the docs neither confirm nor deny
     (does event X fire in case Y? does `updatedAt` move on comments?) is a
     question plus a hello-world step that observes it. Never guess it into
     `same` from GitHub behavior.
4. **Write the brief** from the template in full. Every Origin cell names an
   `operationId`, a slug, or an `llms-full.txt` anchor. Sizes are S, M, or L,
   never time.
5. **Close with the questions**, pruned to what discovery left open. The
   first is always native or mirror, because it decides whether the app
   receives events at all.
6. **Check the brief and fix.** Copy this list, tick each line, fix what
   fails, and repeat until a pass changes nothing.

   - [ ] Every Origin cell names an `operationId`, slug, or anchor that
         exists in the files fetched in step 1.
   - [ ] Every `gap` row has a feedback entry, and the entry quotes one of the five
         tradeoff tests in `gap-bar.md`.
   - [ ] Every `unknown` row has a question in § 7.
   - [ ] No row `origin-isms.md` labels `reshaped` is labeled `gap`; every
         `not-available` row has a question.
   - [ ] Every event the code handles has a § 4 row for each payload field
         it reads, including log-only fields.
   - [ ] Calls the framework makes on the app's behalf appear as rows.
   - [ ] The scopes line equals the union of `x-origin-scopes.scopes` over
         the § 3 operations.
   - [ ] Question 1 is native or mirror.

## Not in scope

Writing port code or adapters. Choosing a language, framework, or client.
Estimating in time. Asking for anything the codebase contains. Sending gap
feedback to Cursor yourself; the brief carries it and the team sends it.

## Reference files

| File | Read when |
| --- | --- |
| `origin-api` skill (install both) | First. Sources and fundamentals. |
| `references/discovery.md` | Scanning the codebase. |
| `references/spec-mapping.md` | Building the index. Matching calls, events, and fields. |
| `references/origin-isms.md` | Labeling a missing GitHub feature. |
| `references/gap-bar.md` | Deciding whether a difference is feedback for Cursor, and writing the entry. |
| `references/brief-template.md` | Writing the output. |
