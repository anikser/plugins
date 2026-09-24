---
name: origin-api
description: >-
  Guides building on the Cursor Origin API: creating an Origin App,
  authenticating as it, calling the REST API, receiving webhooks. Use whenever
  code or a plan touches Origin endpoints, installation tokens, scopes, webhook
  subscriptions or signatures, page tokens, or an Origin App manifest. Points
  at the docs section that answers each question and names the few rules that
  GitHub habits get wrong.
license: MIT
compatibility: >-
  Needs network access to https://cursor.com/docs/api/origin/* at run time.
---

# Build on the Origin API

The docs are the only source of truth. This skill tells you where to look and
which rules to check first. It restates nothing you can read there.

## Fetch first. Never name an endpoint, scope, slug, header, or limit from memory.

- `https://cursor.com/docs/api/origin/openapi.yaml`: the contract. Its
  `x-origin-*` extensions are summarized under `#endpoint-reference`.
- `https://cursor.com/docs/api/origin/llms-full.txt`: the prose reference.
  Anchors below are sections of this file.
- `https://cursor.com/docs/api/origin/llms.txt` (index) and
  `https://cursor.com/docs/api/origin/changelog` (what moved).

Lookup order: for one question, read `llms.txt` to find the section, then
fetch only that section of `llms-full.txt` or the page it links. Fetch the
whole `llms-full.txt` or `openapi.yaml` only when the task needs broad
coverage, such as a porting brief.

Cite `operationId`s and `llms-full.txt` anchors. If this file and the fetched
docs disagree, the docs win.

## Where to look

| Question | Section of `llms-full.txt` |
| --- | --- |
| Which credential for which call; how to mint and how long it lives | `#authentication` through `#git-https-authentication` |
| Install flow and the callback receipt | `#installation`, `#installation-receipt` |
| Which scope an operation needs | `x-origin-scopes` on the operation; `#scopes` for the table and the rules |
| What an installation can do on a mirrored repository | `#mirrored-repositories` |
| Webhook headers, signature, envelope, retries, pausing, recovery | `#webhooks` and its subsections |
| Which events exist and which are delivered without subscribing | `#events` |
| Payload shapes and the `x-origin-webhook-events` extension | `#event-payloads` |
| Pagination, errors, request IDs, repository paths | `#common-conventions` |
| ID form and stability | `#ids` |
| What a `PREVIEW` badge means | `#preview` |
| Rate limits and headers | `#rate-limits` |
| Check-run keys, attempts, stale writes | `#check-runs` |
| What is not there yet | `#current-limitations` |
| A checklist to build against | `#implementation-checklist` |

## Rules to check first

In priority order. Each is one line in the docs; getting it wrong costs a
week.

1. **Native or mirror.** Confirm the target repositories are Origin-native
   or stable outbound mirrors before anything else. On any other mirror
   state an installation can only read, and pushes are not delivered
   (`#mirrored-repositories`, `#events`).
2. **Subscribe.** Only the `installation.*` events arrive without a
   subscription. `#events` says what else delivery needs; a missing
   subscription is silence, not an error.
3. **Verify, dedupe, acknowledge.** Verify the signature over the raw body
   before parsing, dedupe on the delivery ID, return `2xx`, then process
   (`#signature-verification`, `#retries`, `#automatic-disable`). The digest
   step differs from the Standard Webhooks spec, so do not assume a generic
   verifier passes.
4. **Scopes from the spec.** Request the union of `x-origin-scopes.scopes`
   over the operations the app calls, and nothing else (`#scopes`).
5. **Opaque tokens and IDs.** Page tokens and IDs are not yours to build or
   parse (`#pagination`, `#ids`).

## Coming from GitHub

Several GitHub conventions map differently on Origin. The
`port-github-app-to-origin` skill in this plugin covers the differences.
