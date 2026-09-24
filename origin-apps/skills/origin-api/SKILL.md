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

- `https://cursor.com/docs/api/origin/openapi.yaml`: the contract. Every
  operation carries `x-origin-scopes`; every webhook payload schema carries
  `x-origin-webhook-events`, the list of slugs that deliver it.
- `https://cursor.com/docs/api/origin/llms-full.txt`: the prose reference.
  Anchors below are sections of this file.
- `https://cursor.com/docs/api/origin/llms.txt` (index) and
  `https://cursor.com/docs/api/origin/changelog` (what moved).

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
| Payload shapes | `#event-payloads` and the schema's `x-origin-webhook-events` |
| Pagination, errors, request IDs, repository paths, ID form | `#common-conventions` |
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
   subscription. Select every other event the app needs; a missing
   subscription is silence, not an error (`#events`).
3. **Verify, dedupe, acknowledge.** Verify the signature over the raw body
   before parsing, dedupe on the delivery ID, return `2xx`, then process
   (`#signature-verification`, `#retries`, `#automatic-disable`). The digest
   step differs from the Standard Webhooks spec, so do not assume a generic
   verifier passes.
4. **Scopes from the spec.** Request the union of `x-origin-scopes.scopes`
   over the operations the app calls, and nothing else (`#scopes`).

## Coming from GitHub

Origin does not have these. Build the Origin idiom instead of emulating the
GitHub one. Until the docs carry this list, it lives here:

- Issues. Conversation is pull request comments, threads, reviews, labels.
- Commit statuses. Check runs with a stable `key` (`#check-runs`).
- GraphQL. REST only.
- Per-repository webhook CRUD. Subscriptions are app settings.
- User, email, team, or member directory. Actors are IDs, plus a handle
  where the payload exposes one.
- `/user`-style flows. Discover repositories through the installation.
- Reviews keyed by commit SHA. Reviews reference a pull request version.
- Numeric IDs and page numbers. IDs and page tokens are opaque strings; do
  not parse or construct them, and cache repository IDs rather than slugs
  (`#repository-paths`, `#pagination`).
