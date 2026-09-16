# Reading the Origin spec and matching GitHub surface to it

The mapping in the brief is derived from the live `openapi.yaml`, not from a
table in this skill. This file explains what the spec carries and how to match
against it. Build the index once at the start of the run; every later step
looks things up in it.

## What the spec carries

`https://cursor.com/docs/api/origin/openapi.yaml` is OpenAPI 3.1 generated from
Origin's protobuf contract. Beyond the standard fields, four extensions matter
for porting:

| Extension | Where | Meaning |
| --- | --- | --- |
| `x-origin-scopes` | every operation | `scopes`: the scope strings the operation requires. `tokenTypes`: which credentials it accepts (`app` JWT, `installation` token, `user`). `ambient: true`: the scopes come with the credential itself, so an app has nothing to request for it. |
| `x-origin-webhook-events` | payload schemas under `components.schemas` | The event slugs that deliver this payload shape. A schema carrying it is a webhook payload family; the slugs are the only authoritative list of subscribable events. |
| `x-origin-webhook-resource` | payload schemas, when present | Points at the REST component the payload embeds (the object a `Get…` operation returns). When absent, infer the embedded resource from the payload's `$ref` properties. Do not assume every payload has a REST twin; pushes, deletions, and reviewer requests are event-native. |
| `x-cursor-visibility: PREVIEW` | some operations | Published but badged preview. Carry the badge into the brief; a preview operation is usable, but tell the team the shape may still move. |

Everything else you need is standard: `paths` with `operationId`,
`description`, `parameters`, request and response schemas, and `example`
blocks; `components.schemas` with field descriptions that are the contract
text itself.

`llms-full.txt` adds what the spec cannot: the installation flow, the receipt
and app JWT, installation tokens and Git HTTPS, the scopes table, the mirrored
repositories rule, webhook headers, signature verification, the delivery
envelope, retries and recovery, pagination and error conventions, and the
current limitations list. Read those sections before mapping; several rows in
the brief (auth, receiver, pagination) map onto them rather than onto an
operation.

## Build the index

Parse the YAML and produce four lookups. Keep them in a scratch file; the
brief cites from them.

1. **Operations**: for each path and method, record `operationId`, method,
   path template, first sentence of `description`, `x-origin-scopes`
   (`scopes`, `tokenTypes`, `ambient`), `x-cursor-visibility` if any, path and
   query parameter names, request body top-level fields, and the response
   component name.
2. **Webhook events**: for each schema with `x-origin-webhook-events`, record
   each slug → schema name → the properties and their `$ref`s (or the
   `x-origin-webhook-resource` target). Also read the Events table in
   `llms-full.txt` § Webhooks reference for each slug's trigger sentence and
   for which events are app-lifecycle (always delivered) versus repository
   subscriptions (must be selected in app settings).
3. **Scopes**: the union of every `scopes` value seen in `x-origin-scopes`,
   annotated with which operations require it, plus the Scopes table in
   `llms-full.txt` for the human description and the `write` ⊃ `read` rule.
   Separate the scopes an installation can request from those that are
   ambient or user-credential-only; the latter tell you which GitHub flows
   have no app-side equivalent by construction (for example, app creation and
   installation-repository changes are admin actions on Origin, not app
   calls).
4. **Resources**: component schemas returned by `Get…`/`List…` operations,
   with their field names. Used to answer "which fields does the Origin object
   carry" when mapping payload fields and response fields the code reads.

## Matching rules

Match in this order and stop at the first rule that yields a confirmed
counterpart. "Confirmed" means you read the Origin operation's description and
parameters and they answer the same question the GitHub call answers. A name
match is a candidate, never a result.

### REST calls

1. **Normalize the GitHub path** and look for the same shape under
   `/v1/origin`: `/repos/{owner}/{repo}` → `/v1/origin/repos/{ownerSlug}/{repoName}`;
   `{pull_number}` → `{pullNumber}`; `{ref}`/`{sha}` stay; GitHub's
   `check-runs`, `check-suites`, `compare/{basehead}`, `contents`, `git/…`,
   `pulls/{n}/{files,commits,reviews,comments,requested_reviewers,merge}`,
   `labels`, `branches`, `commits` all have direct or near-direct shapes.
   Custom-verb operations on Origin use a `:verb` suffix
   (`…/contents:batchGet`, `…/check-runs:batchUpsert`, `…:grep`).
2. **Re-home GitHub's issue-flavored PR calls.** GitHub puts PR conversation
   comments under `/issues/{n}/comments` and labels under `/issues/{n}/labels`;
   on Origin those live under `/pulls/{n}/…`. This is a path change, not a
   gap, when the code only ever uses them on pull requests. When the code
   uses them on real issues, see `origin-isms.md` (issues are not an Origin
   surface).
3. **Re-home app and installation calls.** GitHub's `/app`,
   `/app/installations`, `/app/installations/{id}/access_tokens`,
   `/installation/repositories` have Origin counterparts under `/v1/origin/app…`
   and `/v1/origin/installation/repos`; check `tokenTypes` to confirm which
   credential each takes. GitHub's `/user`, `/user/installations`,
   `/orgs/{org}/…`, `/search/…`, and `/repositories/{id}` have no path
   counterpart; consult `origin-isms.md` and the Authentication section
   before deciding whether they are absent by design, covered by a different
   idiom, or a gap.
4. **Compare parameters, not just paths.** A matching path with a missing
   filter the code depends on (for example a list the code narrows by a field
   Origin does not accept) is `workaround` or `gap`, not `same`. Read the
   `parameters` block.
5. **Compare response fields the code reads.** Trace which response
   properties the handlers dereference and check them against the Origin
   component. Missing fields are common where GitHub inlines convenience data
   (web URLs, nested user profiles, aggregate counts). Each missing field gets
   its own line under the row: follow-up call, derivable, or absent.

### GraphQL

There is no GraphQL endpoint. Decompose each query or mutation into the REST
reads and writes it stands for, then map those individually. Note the fan-out
(one query → N calls) as the tradeoff on the row. If the query exists to
avoid REST pagination or to fetch a cross-repository view, say so; that is
the tradeoff the team weighs.

### Permissions → scopes

GitHub permissions are `<noun>: read|write`; Origin scopes are
`repository:<noun>[:<subnoun>]:<read|write>` with `write` implying `read`
and `repository:metadata:read` granted automatically. Match the noun, then
verify by finding the operations the code actually calls in the Operations
lookup and reading *their* `x-origin-scopes` — the scope set in the brief is
the union of what the called operations require, not a translation of the
manifest. GitHub permissions with no Origin noun (`statuses`, `issues`,
`members`, `organization_*`, `pages`, `actions`, `workflows`, `secrets`,
`deployments`, `environments`) go through `origin-isms.md` before they can be
called gaps.

### Webhook events → slugs

Origin slugs are `<resource>[.<sub-resource>].<past-tense-action>` with the
action in the slug, never in the payload: GitHub's single `pull_request` event
with an `action` field is several Origin events. Translate each
`event.action` pair the code handles into a candidate slug, then confirm the
slug appears in the Webhook events lookup. Candidates that do not appear are
not events on Origin; check whether the state change is observable another
way (an event on a related resource, or a REST read on receipt of one) before
classifying. Installation lifecycle events are always delivered to the app;
everything else must be subscribed explicitly, which the brief's hello-world
path calls out.

### Payload fields → schema properties

For each field path a handler reads off a GitHub payload
(`payload.pull_request.head.sha`, `payload.repository.full_name`,
`payload.sender.login`, `payload.commits[].added`), find the Origin payload
schema for the mapped slug and walk its properties. Record one of:

- **present** at `<origin.path>`;
- **follow-up read**: not in the payload, available from `<operationId>` using
  identifiers the payload does carry;
- **derivable**: assembled from present fields (say how, and note whether the
  format is contractual);
- **absent**: no payload field and no read that yields it (this row goes to
  the gap bar).

The payload carries references (`repository`, `pullRequest`) around the
snapshot of the one object that changed. Expect a lean shape and plan the
follow-up reads; that is the Origin design, not a defect
(`origin-isms.md` § Webhooks). Compare the webhook snapshot's schema with
the REST resource it mirrors: a field on the REST component that the webhook
twin lacks (for example a list the resource carries but the snapshot omits)
is a follow-up read via the matching `Get…`, and the code that reads it off
the GitHub payload today needs that read on every event.

### Out-of-domain surfaces and spec-silent behavior

Some of what a GitHub App touches is not source control at all: Marketplace
billing and plan lookups, merge queues, Actions, Pages, Projects,
Milestones, Discussions, `github.com` HTML probes. When neither the spec nor
`llms-full.txt` mentions the concept, the row is `unknown` with an up-front
question about what the team wants on Origin, never `gap` (Origin has not
declined it; the team may not need it) and never `by-design-absent` (only
`origin-isms.md` rows earn that).

When the code depends on a behavior the docs do not state (does an event
fire for a pull request opened as a draft? does `updatedAt` move on a
comment? what does a remove return when nothing was there?), do not resolve
it from GitHub's behavior. Record the dependency in the row's Open question
column and add a step to the hello-world path that observes it on a native
repository.

## Provenance in the brief

Write the spec's `info.version`, the fetch timestamp, and the four URLs into
the brief's provenance block. State plainly that the brief reflects the
surface on that date and that the team should re-read the changelog before
acting on any row marked `workaround` or `gap`, because those are the rows
most likely to have moved.
