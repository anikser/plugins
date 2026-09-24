---
name: origin-api
description: >-
  Routes questions about the Cursor Origin API to the right section of the
  Origin docs and names the few rules to check first. Use when a task mentions
  Origin, the Origin API, Origin Apps, or Origin webhooks, including creating
  an Origin App, authenticating as one, calling Origin endpoints, or handling
  Origin webhook deliveries.
license: MIT
compatibility: >-
  Needs network access to https://cursor.com/docs/api/origin/* at run time.
---

# Origin API

The docs are the source of truth. This skill says where to look and which
rules to check first; it does not restate the docs.

## Fetch first

Do not name an endpoint, scope, event slug, header, or limit from memory.

- `https://cursor.com/docs/api/origin/openapi.yaml`: the contract. Its
  `x-origin-*` extensions are summarized under `#endpoint-reference`.
- `https://cursor.com/docs/api/origin/llms-full.txt`: the prose reference.
  Anchors below are sections of this file.
- `https://cursor.com/docs/api/origin/llms.txt` (index) and
  `https://cursor.com/docs/api/origin/changelog` (what moved).

For one question, use `llms.txt` to find the section, then read only that
section. Fetch the whole `llms-full.txt` or `openapi.yaml` when the task
needs broad coverage, such as a porting brief.

Cite `operationId`s and `llms-full.txt` anchors. Where this file and the docs
disagree, the docs win.

## Where to look

| Question | Section of `llms-full.txt` |
| --- | --- |
| Which credential for which call; minting and lifetime | `#authentication` through `#git-https-authentication` |
| Install flow and the callback receipt | `#installation`, `#installation-receipt` |
| Which scope an operation needs | `x-origin-scopes` on the operation; `#scopes` |
| What an installation can do on a mirrored repository | `#mirrored-repositories` |
| Webhook headers, signature, envelope, retries, pausing, recovery | `#webhooks` |
| Which events exist and which arrive without subscribing | `#events` |
| Payload shapes | `#event-payloads` |
| Pagination, errors, request IDs, repository paths | `#common-conventions` |
| ID form and stability | `#ids` |
| What a `PREVIEW` badge means | `#preview` |
| Rate limits | `#rate-limits` |
| Check-run keys, attempts, stale writes | `#check-runs` |
| What is not there yet | `#current-limitations` |
| A checklist to build against | `#implementation-checklist` |

## Rules to check first

1. **Native or mirror.** Confirm the target repositories are Origin-native
   or stable outbound mirrors. On any other mirror state an installation can
   only read, and pushes are not delivered (`#mirrored-repositories`,
   `#events`).
2. **Subscribe.** Only the `installation.*` events arrive without a
   subscription; a missing subscription is silence, not an error (`#events`).
3. **Verify, dedupe, acknowledge.** Verify the signature over the raw body
   before parsing, dedupe on the delivery ID, return `2xx`, then process
   (`#signature-verification`, `#retries`, `#automatic-disable`). The digest
   step differs from the Standard Webhooks spec; do not assume a generic
   verifier passes.
4. **Scopes from the spec.** Request the union of `x-origin-scopes.scopes`
   over the operations the app calls (`#scopes`).
5. **Opaque tokens and IDs.** Do not build or parse page tokens or IDs
   (`#pagination`, `#ids`).

Porting an existing GitHub App: the `port-github-app-to-origin` skill in
this plugin covers how its capabilities map onto Origin.
