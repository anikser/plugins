---
name: origin-api
description: >-
  Build on the Cursor Origin API. Create an Origin App, authenticate as it,
  call the REST API, receive webhooks. Use whenever code or a plan touches
  Origin endpoints, installation tokens, scopes, webhook subscriptions or
  signatures, page tokens, or an Origin App manifest. Lists the sources to
  fetch first and the Origin rules that GitHub habits get wrong.
license: MIT
compatibility: >-
  Needs network access to https://cursor.com/docs/api/origin/* at run time.
---

# Build on the Origin API

## Fetch first. Never name an endpoint, scope, slug, or header from memory.

- `https://cursor.com/docs/api/origin/openapi.yaml` is the contract. Every
  operation carries `x-origin-scopes` (`scopes`, `tokenTypes`, `ambient`).
  Every webhook payload schema carries `x-origin-webhook-events`, the only
  authoritative list of subscribable slugs.
- `https://cursor.com/docs/api/origin/llms-full.txt` covers the installation
  flow, authentication, the scopes table, mirrored repositories, webhook
  headers and verification, the delivery envelope, retries, pagination,
  errors, and current limitations.
- `https://cursor.com/docs/api/origin/llms.txt` is the index.
  `https://cursor.com/docs/api/origin/changelog` says what moved.

Cite `operationId`s and `llms-full.txt` anchors. If this file and the fetched
docs disagree, the docs win.

## Rules GitHub habits get wrong

- **Check native or mirror before anything else.** Apps get full scopes only
  on Origin-native repositories. A repository mirrored from GitHub returns
  `403` on every write and never delivers `repository.pushed`. The ping
  succeeds and then nothing else arrives.
- **Only installation lifecycle events are delivered by default.** Select
  every other event in app settings. An unselected event is silence, not an
  error.
- **Signature `v1ed` is Ed25519 over a SHA-256 digest of the raw body**, with
  keys from Origin's JWKS. It matches Standard Webhooks except for the digest,
  so off-the-shelf verifiers fail unmodified. Verify the raw body before
  parsing. Reject `webhook-timestamp` more than five minutes off. Headers are
  `webhook-*`, not `x-github-*`. After verification the body is authoritative.
- **`deliveryId` is the idempotency key.** It is stable across retries.
  `event.id` identifies the domain event. Return `2xx` after verification and
  process asynchronously, because persistent failure pauses delivery for the
  app.
- **Payloads are lean snapshots** of the one object that changed, plus
  references to its containers. No changed-file lists, before-SHAs, web URLs,
  or inlined profiles. Follow up with the `Get…` for the object and count the
  fan-out. The action is in the slug (`pull_request.review.submitted`). There
  is no `action` field.
- **The installation receipt JWT proves consent. It is never a Bearer token.**
  Its `sub` is the installation ID.
- **The app JWT is EdDSA over Ed25519, not RS256.** Register only the public
  key.
- **Installation tokens are short-lived. Mint them just in time** from the
  app JWT and attenuate to the scopes and `repositoryIds` the job needs (IDs,
  not slugs). Git over HTTPS uses Basic auth with user `x-access-token` and
  the token as password. Bearer is REST only.
- **Scopes come from the operations you call.** Request the union of their
  `x-origin-scopes.scopes`. `write` implies `read`. `repository:metadata:read`
  is automatic. `ambient: true` needs no request. Operations whose
  `tokenTypes` is user-only (create app, add repositories to an installation,
  mirror transitions) have no app-side path, and there is no `/user` analog.
- **Page tokens are opaque and bound to the resource and filters.** Never
  construct, parse, or reuse one across filter changes. Send `pageSize` on
  every request, including continuations. There is no `Link` header and no
  total.
- **IDs are TypeIDs** (`repo_…`, `i_…`, `cmt_…`), never integers. Cache IDs,
  not slugs. `/repos/_/{repoId}` survives renames. 64-bit integers (PR
  numbers, versions) are JSON strings. Defaults are present (`false`, `0`,
  `[]`), so a present `false` is a value.
- **`404` means not found or no access.** Branch on status and `code`, never
  on message text. Quote `X-Request-ID` when escalating.
- **The rate limit is a per-principal point budget.** Honor `Retry-After` on
  `429`. Git HTTPS is metered separately. Cursor raises per-app budgets on
  request.
- **These are decisions, not gaps.** No commit statuses (check runs upsert on
  a caller-stable `key`). No Issues (conversation is PR comments, threads,
  reviews, and labels). No GraphQL. No per-repository webhook CRUD. No user or
  email directory. Reviews anchor to a pull request version, not a SHA. A
  thread materializes from its first diff-anchored comment.
