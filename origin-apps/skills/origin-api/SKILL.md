---
name: origin-api
description: >-
  Build on the Cursor Origin API: create an Origin App, authenticate as it,
  call the REST API, receive webhooks. Use whenever code or a plan touches
  Origin endpoints, installation tokens, scopes, webhook subscriptions or
  signatures, page tokens, or an Origin App manifest. Points at the live docs
  and spec first and carries only the practices that do not change between
  spec versions.
license: MIT
compatibility: >-
  Needs network access to https://cursor.com/docs/api/origin/* at run time.
---

# Build on the Origin API

Origin is Cursor's code forge. Its API is GitHub-shaped (repos, pull requests,
reviews, comments, check runs, labels, branches, commits) and deliberately not
GitHub-compatible on the wire. This skill tells you where the contract lives
and what stays true across versions of it. It does not restate endpoints,
schemas, scope strings, or event slugs; those come from the spec you fetch.

## Fetch the spec; do not trust memory

Before naming any endpoint, scope, event slug, header, or field, fetch:

- `https://cursor.com/docs/api/origin/llms.txt` — index of the docs
- `https://cursor.com/docs/api/origin/openapi.yaml` — the contract (OpenAPI
  3.1). Every operation carries `x-origin-scopes` (`scopes`, `tokenTypes`,
  `ambient`); every webhook payload schema carries `x-origin-webhook-events`
  (the slugs that deliver it) and often `x-origin-webhook-resource`;
  `x-cursor-visibility: PREVIEW` marks operations whose shape may still move.
- `https://cursor.com/docs/api/origin/llms-full.txt` — the prose the spec
  cannot carry: installation flow, authentication, scopes table, mirrored
  repositories, webhook headers and signature verification, delivery
  envelope, retries, pagination, errors, current limitations
- `https://cursor.com/docs/api/origin/changelog` — what moved recently

Cite `operationId`s and `llms-full.txt` anchors in anything you write. Record
`info.version` and the fetch time when the output will outlive the session.
Where this file and the fetched docs disagree, the docs win.

## Practices that hold across spec versions

### Credentials

- Three principals, in order of power: **user** credential (admin actions:
  create the app, add repositories to an installation, mirror transitions),
  **app** JWT (EdDSA over Ed25519; register only the public key; identifies
  the app to app-level operations), **installation** token (`oit_…`,
  short-lived, minted from the app JWT for one installation; the credential
  for repository work). Check an operation's `x-origin-scopes.tokenTypes` to
  see which it accepts.
- Mint installation tokens just in time and let them expire; never persist
  one as a long-lived secret. Attenuate at mint time to the scopes and
  `repositoryIds` the job needs (IDs, not slugs).
- The installation **receipt** JWT returned from the install redirect proves
  consent and carries the installation ID. It is never a Bearer token.
- Git over HTTPS uses Basic auth with username `x-access-token` and an
  installation token as the password; Bearer is for REST only.

### Scopes

- Scopes are `repository:<noun>[:<sub>]:<read|write>`; `write` implies `read`;
  `repository:metadata:read` comes with every installation.
- Request the union of `x-origin-scopes.scopes` across the operations you
  actually call, nothing more. An installation can only narrow what the admin
  approved, so an over-broad manifest is a review burden, not a convenience.
- `ambient: true` means the credential already carries the scope; there is
  nothing to request for it.

### Repositories

- Apps act on Origin-native repositories. A repository mirrored *from* GitHub
  is read-only to an installation (writes return `403`) and does not deliver
  `repository.pushed`, because GitHub already notifies apps for it. Confirm
  native-or-mirror before anything else; a mirror produces a successful ping
  and then silence.

### Webhooks

- Only installation lifecycle events are delivered by default. Every other
  event must be selected in app settings. Take the slug list from
  `x-origin-webhook-events`, not from GitHub habit.
- Verify before parsing. Scheme `v1ed`: Ed25519 over a SHA-256 digest of the
  raw body, keys from Origin's JWKS (cache per `Cache-Control`; keys rotate).
  Reject `webhook-timestamp` more than five minutes off. It follows Standard
  Webhooks except for signing a digest, so off-the-shelf verifiers do not
  validate it unmodified. Routing headers are `webhook-*`, not `x-github-*`;
  after verification the body is authoritative.
- Handle idempotently. `deliveryId` in the envelope is stable across retries
  and is the dedupe key; `event.id` identifies the domain event. Delivery is
  at-least-once.
- Acknowledge fast, process later. Retries follow a schedule and persistent
  failure pauses delivery for the app; the recovery window is finite and
  redelivery is through the deliveries operations, so a slow handler costs
  you events. Return `2xx` after verification and enqueue.
- Payloads are lean snapshots of the one object that changed, plus compact
  references to its containers. No changed-file lists, before-SHAs, web URLs,
  or inlined profiles. The intended pattern is a follow-up `Get…` with the
  identifiers the payload carries; count that fan-out when you design.
- The action lives in the slug (`pull_request.created`,
  `pull_request.review.submitted`); there is no `action` field and no
  `previous_attributes` delta.

### Pagination

- `pageSize` / `pageToken` / `nextPageToken`. Tokens are opaque and bound to
  the resource and filters: never construct, parse, persist across filter
  changes, or share them between requests with different parameters.
- Pass `pageSize` on every request, including continuations; do not rely on
  the token to remember it. No `Link` header, no page numbers, no total count.
  Loop until `nextPageToken` is absent or empty.

### Identifiers and wire shape

- IDs are opaque prefixed TypeIDs (`app_…`, `i_…`, `repo_…`, `user_…`,
  `cmt_…`). Never integers, never derived. Cache IDs, not slugs; a repository
  is addressable as `/repos/_/{repoId}`, which survives renames.
- camelCase JSON; 64-bit integers (PR numbers, versions) are JSON strings;
  RFC 3339 timestamps; defaults are present (`false`, `0`, `""`, `[]`), so a
  present `false` is a value and a missing key is only the default when the
  field is documented optional.
- Public terminology is "pull request"; do not look for "change" on the wire.

### Errors

- One envelope: `google.rpc.Status` `{code, message, details}` with typed
  `details` (`BadRequest` field violations, `RequestInfo` with the request
  id; more types may appear, so tolerate unknown ones). `X-Request-ID` is on
  every error; quote it when escalating.
- `404` does not distinguish not-found from no-access. Branch on HTTP status
  and `code`, never on message text.

### Rate limits

- A per-principal point budget: read `X-RateLimit-*` on every response and
  honor `Retry-After` on `429`. Git over HTTPS is metered separately
  (`X-RateLimit-Resource: git`). Cursor raises per-app budgets on request;
  ask rather than spinning.

### Deliberate differences from GitHub

Design decisions, not gaps. Build the Origin idiom instead of emulating the
GitHub one:

- **No commit statuses.** Check runs are the one status primitive; they upsert
  on a caller-stable `key` and rulesets bind on that key.
- **No Issues.** Conversation is pull request comments, threads, reviews, and
  labels on pull requests.
- **No GraphQL.** REST only; decompose queries and accept the fan-out.
- **No per-repository webhook CRUD.** Subscriptions are app settings.
- **No user or email directory**, no team pages; actors are TypeIDs (plus a
  handle where the contract exposes it).
- **Reviews anchor to a pull request version**, not a commit SHA.
- **No standalone threads API.** A thread materializes from its first
  diff-anchored comment.

## Hello-world path

Create the app (form or user-credential `CreateApp`) → register the Ed25519
public key → select webhook events → install on an Origin-native repository →
verify the ping signature → mint an installation token → first `Get…` → first
real event. Each arrow is a step to observe, not code to write; when a step
is silent, the answer is almost always native-or-mirror or an unsubscribed
event.

## Related skill

`port-github-app-to-origin`, in this plugin, applies these fundamentals to
an existing GitHub App: it discovers the app's GitHub surface from code, maps
it onto the spec, and writes a porting brief. Use it for a port; use this
skill for everything else on Origin.
