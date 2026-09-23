# Origin-isms: where Origin departs from GitHub on purpose

Origin uses GitHub's nouns and general shape and deliberately not its wire
format. When a GitHub feature has no counterpart in the spec, check this list
before calling it a gap: a row here is `by-design-absent` (or `reshaped`) in
the brief, and the brief's job is to point the team at the Origin idiom. Each
entry gives the departure, the idiom, and the reason in one line, so you can
explain it to a team that has only ever seen GitHub. Confirm the current
wording in `llms-full.txt`; this file explains intent, the docs state the
contract. The `origin-api` skill carries the same conventions as practices
for building; this file carries them as parity decisions for a port.

## Which repositories an app can act on

- **Apps act on Origin-native repositories (and stable outbound mirrors).** A
  repository mirrored *from* GitHub is read-only to an installation — metadata
  and contents reads, clone/fetch/pull — and rejects pull requests, reviews,
  comments, checks, rulesets, and every write with `403`. Why: a write on a
  mirror would have to act on GitHub as Cursor's GitHub App, with risk Origin
  cannot bound; and GitHub already sends its own webhooks for those repos.
- **`repository.pushed` is not delivered for GitHub-mirrored repos.** Why:
  GitHub owns those pushes and already notifies the app; Origin would
  duplicate them. Consequence for the port: a ping works on a mirror and then
  nothing else does. The first up-front question in every brief is
  native-or-mirror for exactly this reason.
- **`mirror.status` does not tell you whether writes are allowed.** Treat the
  `403` as authoritative.

## Identity and authentication

- **No OAuth-app token exchange as the install path.** Install is a consent
  redirect that returns a signed **installation receipt** JWT (`sub` = the
  installation ID, `state` echoed) instead of `installation_id` and
  `setup_action` query parameters. Why: the receipt proves the approval came
  from Origin; a bare query string cannot. The receipt is never a Bearer
  token.
- **App JWT is EdDSA over Ed25519, not RS256.** Register only the public key;
  up to ten active keys. `kid` and `iss` are the app ID; `aud` is fixed.
- **Installation tokens are `oit_…`, short-lived, minted just in time**, and
  can be attenuated to fewer scopes or to specific `repositoryIds` (IDs, not
  slugs — resolve the ID first). Git over HTTPS uses Basic auth with username
  `x-access-token` and the token as password; Bearer belongs to REST only.
- **User-scoped calls (`/user`, `/user/installations`, install-by-user) have
  no app-side counterpart.** Repository discovery is through the
  installation (`/installation/repos`), and app creation, adding
  repositories to an installation, and mirror transitions are admin actions
  carried by a Cursor user credential, not app calls. Read the live
  Authentication section for the current user-credential story before
  labeling anything here; do not assume a GitHub-OAuth analog exists.
- **Scopes, not permissions.** `repository:<noun>[:<sub>]:<read|write>`;
  `write` implies `read`; `repository:metadata:read` is automatic; the
  installation can only narrow what the admin approved. Look each called
  operation's requirement up in `x-origin-scopes` rather than translating the
  manifest noun-for-noun.

## Wire conventions

- **Opaque TypeIDs, never integers**: `app_…`, `i_…`, `ns_…`, `repo_…`,
  `user_…`, `cmt_…`, `evt_…`. Why: sequential IDs are enumerable; opaque IDs
  are the stable handle to cache. A repository is addressable by ID as
  `/repos/_/{repoId}`, which survives renames; there is no
  `/repositories/{id}` route and no numeric ID anywhere.
- **camelCase JSON; 64-bit integers (PR numbers, version numbers) are JSON
  strings; RFC 3339 timestamps.**
- **Defaults are present, not omitted.** `false`, `0`, `""`, `[]` appear in
  bodies; only fields documented as optional are absent when unset. Do not
  treat a missing key as the default and do not treat a present `false` as
  "unset".
- **Pagination is `pageSize` / `pageToken` / `nextPageToken`.** Tokens are
  opaque, bound to the resource and filters, and there is no `Link` header,
  no `page`, no total count. Why: keyset cursors do not skip or duplicate
  under concurrent writes; offsets do. Restart when filters change.
- **Errors are one envelope**: `google.rpc.Status` `{code, message, details}`
  with typed `details` (`BadRequest` field violations, `RequestInfo` request
  id on every error; further typed detail types such as machine-readable
  `ErrorInfo` reasons may be added, so read the live Errors section and
  tolerate unknown detail types). `X-Request-ID` is on every error. **`404`
  never distinguishes not-found from no-access.** Why: anti-enumeration.
  Branch on status and `code`; quote the request id when escalating.
- **No GraphQL.** REST only; decompose queries.
- **Rate limits are a per-principal point budget**, `X-RateLimit-*` plus
  `Retry-After` on `429`; Git HTTPS meters separately (`X-RateLimit-Resource:
  git`). Cursor can raise per-app budgets on request.
- **Public terminology is "pull request"** throughout; do not expect
  "change" or "changeset" on the wire.

## Resources GitHub has that Origin does not reproduce

- **No commit statuses.** Check runs are the only status primitive:
  `PostCheckRun` upserts on a caller-stable `key` (with `externalId` /
  `externalUpdatedAt` for retries and ordering), and rulesets bind on check
  keys. Why: one status model, idempotent by construction. A `statuses`
  permission or `POST /statuses/{sha}` maps to checks, not to a gap.
- **No Issues.** Origin's conversation surfaces are pull requests, pull
  request comments and threads, reviews, and labels on pull requests. An
  `issues`-only GitHub App has no Origin equivalent for that part; say so
  and ask what the team wants the PR-scoped behavior to be. GitHub's
  `/issues/{n}/comments` used *on a PR* is just a path change.
- **No repository-level webhook CRUD** (`/repos/…/hooks`). Subscriptions are
  an app-settings concern; there are no per-repo hook objects.
- **No app-manifest conversion endpoint and no OAuth-app token mints.**
  Legacy GitHub mechanisms Origin does not reproduce. App creation is a
  form (which accepts prefill query parameters) or the user-credential
  `CreateApp` operation.
- **No REST git-object writes beyond the documented ones.** Commits are
  pushed over Git HTTPS with an installation token (or created through the
  documented commit-from-files and ref operations); do not expect a GitHub
  Git Data API for arbitrary tree/blob writes.
- **No standalone threads API.** Comments are the only content write
  surface; a thread materializes from its first diff-anchored comment and is
  addressable for resolve/reopen. Why: one write surface, no dual bookkeeping.
- **No user/email directory.** Actors carry a TypeID (and a handle where the
  contract exposes it); there is no lookup from email to user and no team
  or member pages to link to. Why: an email or membership oracle.

## Webhooks

- **One message serves REST and webhooks.** A payload snapshots the one
  object that changed exactly as its `Get…` returns it, plus compact
  references (`repository`, `pullRequest`) for its containers. Why: consumers
  reuse their REST decoders and never see a partially hydrated shape.
- **Webhooks notify; the API answers.** Payloads are lean by design: no
  changed-file lists on pushes, no before-SHA on PR events, no web URLs, no
  inlined user profiles. Follow-up reads (`GetCommit`, `CompareCommits`,
  `ListComparisonFiles`, `GetRepo`, `GetPullRequest`) are the intended
  pattern. Why: no emit-time joins, no size blowups, no staleness races.
  Map fields the code reads to specific follow-up calls and count the
  fan-out honestly; that count is the tradeoff, not a defect.
- **Slugs are `<resource>[.<sub>].<past-tense-action>`** and the action lives
  in the slug (`pull_request.created`, `pull_request.review.submitted`,
  `repository.check_run.completed`), never in a payload `action` field, and
  there is no `previous_attributes` delta. Why: granular event types over
  payload flags; one shape per event. GitHub's `pull_request` +
  `action: synchronize` becomes `pull_request.head_ref.pushed`, and so on —
  confirm each in `x-origin-webhook-events`.
- **Envelope**: `{deliveryId, appId, installationId, event: {id, type,
  eventTime, payload}}`. `deliveryId` is stable across retries and is the
  idempotency key; `event.id` identifies the domain event. Routing headers
  are `webhook-id`, `webhook-timestamp`, `webhook-signature`,
  `webhook-event-type`, `webhook-app-id`, `webhook-installation-id` (not
  `x-github-*`); after verification the body is authoritative.
- **Signature is Ed25519 over a SHA-256 digest, scheme `v1ed`**, keys from
  Origin's JWKS (rotated weekly, cache per `Cache-Control`), not an HMAC
  shared secret. It tracks the Standard Webhooks spec except that it signs a
  digest instead of the raw string, so off-the-shelf Standard Webhooks
  verifiers do not validate it as-is. Verify the raw body before parsing;
  reject timestamps more than five minutes off.
- **Installation lifecycle events are always delivered; every other event
  must be selected in app settings.** Creating the app subscribes to nothing
  else. Why: opt-in exposure. This is the second most common first-week
  stall after mirror-vs-native.
- **Delivery is at-least-once with retries and a seven-day recovery window**
  (`ListWebhookDeliveries`, `BatchRedeliverWebhookDeliveries`); persistent
  failure pauses the app's delivery.

## Checks, reviews, comments

- **Check runs upsert on `key`**, live under a check suite keyed the same
  way, and can be flagged re-requestable; a re-request arrives as an event
  to the owning app. Annotations are appended, not replaced.
- **Reviews anchor to a pull request *version*, not a commit SHA.** Why: a
  SHA can match several versions after a rebase or retarget. Code that keys
  approvals by `commit_id` re-keys by version number.
- **Requested reviewers are addressed by identifier** (users, groups), and
  Origin is deliberately careful about existence oracles on that surface. Do
  not expect `created_via` or team pages on the read side.
- **Find your own writes by a key you control.** Check runs are found by
  their `key`; for reviews and comments, carry a marker the app owns (a body
  prefix, a stable key) rather than relying on actor identity alone, and
  confirm in the spec which author filters the list operations offer.
