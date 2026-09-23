---
name: origin-api
description: >-
  Build on the Cursor Origin API: create an Origin App, authenticate as it,
  call the REST API, receive webhooks. Use whenever code or a plan touches
  Origin endpoints, installation tokens, scopes, webhook subscriptions or
  signatures, page tokens, or an Origin App manifest. Fetch-first sources plus
  the gotchas GitHub instinct gets wrong.
license: MIT
compatibility: >-
  Needs network access to https://cursor.com/docs/api/origin/* at run time.
---

# Build on the Origin API

## Fetch first; never name an endpoint, scope, slug, or header from memory

- `https://cursor.com/docs/api/origin/openapi.yaml` — the contract. Every
  operation carries `x-origin-scopes` (`scopes`, `tokenTypes`, `ambient`);
  every webhook payload schema carries `x-origin-webhook-events`, the only
  authoritative list of subscribable slugs.
- `https://cursor.com/docs/api/origin/llms-full.txt` — installation flow,
  authentication, scopes table, mirrored repositories, webhook headers and
  verification, delivery envelope, retries, pagination, errors, limitations.
- `https://cursor.com/docs/api/origin/llms.txt` (index) and
  `https://cursor.com/docs/api/origin/changelog` (what moved).

Cite `operationId`s and `llms-full.txt` anchors. Where this file and the
fetched docs disagree, the docs win.

## Gotchas

- **Native or mirror, first.** Apps get full scopes only on Origin-native
  repositories. A repository mirrored from GitHub returns `403` on every write
  and never delivers `repository.pushed`; the ping succeeds and then nothing
  else arrives.
- **Only installation lifecycle events are delivered by default.** Select
  every other event in app settings; an unselected event is silence, not an
  error.
- **Signature `v1ed` is Ed25519 over a SHA-256 digest of the raw body**, keys
  from Origin's JWKS. It is Standard Webhooks except for the digest, so
  off-the-shelf verifiers fail unmodified. Verify the raw body before parsing;
  reject `webhook-timestamp` more than five minutes off. Headers are
  `webhook-*`, not `x-github-*`; after verification the body is authoritative.
- **`deliveryId` is the idempotency key** (stable across retries);
  `event.id` is the domain event. Return `2xx` after verification and process
  asynchronously: persistent failure pauses delivery for the app.
- **Payloads are lean snapshots** of the one object that changed plus
  container references: no changed-file lists, before-SHAs, web URLs, or
  inlined profiles. Follow up with the `Get…` for the object; count the
  fan-out. The action is in the slug (`pull_request.review.submitted`); there
  is no `action` field.
- **The installation receipt JWT is proof of consent, never a Bearer token.**
  Its `sub` is the installation ID.
- **App JWT is EdDSA over Ed25519, not RS256.** Register only the public key.
- **Installation tokens are short-lived; mint just in time** from the app JWT
  and attenuate to the scopes and `repositoryIds` the job needs (IDs, not
  slugs). Git over HTTPS is Basic auth, user `x-access-token`, token as
  password; Bearer is REST only.
- **Scopes come from the operations you call**: request the union of their
  `x-origin-scopes.scopes`. `write` implies `read`; `repository:metadata:read`
  is automatic; `ambient: true` needs no request. Operations whose
  `tokenTypes` is user-only (create app, add repositories to an installation,
  mirror transitions) have no app-side path; there is no `/user` analog.
- **Page tokens are opaque and bound to the resource and filters.** Never
  construct, parse, or reuse across filter changes. Send `pageSize` on every
  request, including continuations. No `Link` header, no total.
- **IDs are TypeIDs** (`repo_…`, `i_…`, `cmt_…`), never integers. Cache IDs,
  not slugs; `/repos/_/{repoId}` survives renames. 64-bit integers (PR
  numbers, versions) are JSON strings. Defaults are present (`false`, `0`,
  `[]`), so a present `false` is a value.
- **`404` is not-found *or* no-access.** Branch on status and `code`, never
  message text. Quote `X-Request-ID` when escalating.
- **Rate limit is a per-principal point budget**; honor `Retry-After` on
  `429`. Git HTTPS is metered separately. Per-app raises exist; ask.
- **Deliberate differences, not gaps:** no commit statuses (check runs upsert
  on a caller-stable `key`); no Issues (conversation is PR comments, threads,
  reviews, labels); no GraphQL; no per-repository webhook CRUD; no user or
  email directory; reviews anchor to a pull request *version*, not a SHA; a
  thread materializes from its first diff-anchored comment.
