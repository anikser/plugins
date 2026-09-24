# Reading the Origin spec and matching GitHub calls and events to it

Every mapping in the brief comes from the fetched `openapi.yaml`, not from a
table here. Build the index once. Every later step looks things up in it.

## Extensions the spec carries

| Extension | Where | Meaning |
| --- | --- | --- |
| `x-origin-scopes` | every operation | `scopes` the operation requires. `tokenTypes` it accepts (`app`, `installation`, `user`). `ambient: true` means there is nothing to request. |
| `x-origin-webhook-events` | payload schemas | The slugs that deliver this payload shape. A schema carrying it is a webhook family. These slugs are the only authoritative event list. |
| `x-origin-webhook-resource` | some payload schemas | The REST component the payload embeds. When absent, infer it from `$ref`s. Pushes, deletions, and reviewer requests are event-native with no REST twin. |
| `x-cursor-visibility: PREVIEW` | some operations | Usable. The shape may move. Carry the badge into the brief as a `preview` suffix. |

## Build the index

1. **Operations**: `operationId`, method, path, `x-origin-scopes`,
   visibility, parameter names, top-level request fields, response component.
2. **Webhook events**: slug → schema → properties and `$ref`s (or the
   `x-origin-webhook-resource` target). From `llms-full.txt` § Webhooks,
   which slugs are app-lifecycle (always delivered) versus repository events
   (must be selected).
3. **Scopes**: the union of every `scopes` value, annotated with the
   operations that need it. Separate installation-requestable scopes from
   ambient and user-only ones. The user-only set tells you which GitHub flows
   have no app-side equivalent.
4. **Resources**: component schemas returned by `Get…`/`List…`, with field
   names, for "does the Origin object carry this field".

`scripts/index-origin-spec.py openapi.yaml [ops|events|scopes|schema <Name>]`
prints all four.

## Matching

Match in this order and stop at the first rule that yields a confirmed
counterpart. Confirmed means you read the Origin operation's description and
parameters and it answers the same question the GitHub call answers. A name
match is a candidate, never a result.

**REST calls**

1. Normalize the GitHub path to the same shape under `/v1/origin`
   (`{owner}/{repo}` → `{ownerSlug}/{repoName}`, `{pull_number}` →
   `{pullNumber}`; custom verbs are `:verb` suffixes such as
   `…/contents:batchGet`).
2. Re-home GitHub's issue-flavored pull request calls: `/issues/{n}/comments` and
   `/issues/{n}/labels` used *on a pull request* live under `/pulls/{n}/…`.
   That is a path change, not a gap. When the code uses them on real issues,
   see `origin-isms.md`.
3. Re-home `/app`, `/app/installations`, access-token minting, and
   `/installation/repositories` under `/v1/origin/app…` and
   `/v1/origin/installation/repos`; confirm `tokenTypes`. `/user`,
   `/user/installations`, `/orgs/…`, `/search/…`, and `/repositories/{id}`
   have no path counterpart. Consult `origin-isms.md` before labeling them.
4. Compare parameters as well as paths. A matching path that lacks a filter
   the code depends on is `workaround` or `gap`, not `same`.
5. Compare the response fields the code reads. Each missing field gets its
   own line as follow-up call, derivable, or absent. GitHub inlines web URLs,
   nested profiles, and counts that Origin does not.

**GraphQL.** There is no endpoint. Decompose each document into the REST
reads and writes it stands for, map those, and record the fan-out as the
row's tradeoff.

**Permissions → scopes.** Do not translate the manifest noun-for-noun. Find
the operations the code calls and take the union of *their*
`x-origin-scopes.scopes`. GitHub permissions with no Origin noun
(`statuses`, `issues`, `members`, `organization_*`, `pages`, `actions`,
`workflows`, `deployments`) go through `origin-isms.md` first.

**Events → slugs.** Each GitHub `event` + `action` pair becomes a candidate
slug (`pull_request` plus `synchronize` becomes `pull_request.head_ref.pushed`).
Confirm it exists in the webhook index. A candidate that does not exist is
not an event on Origin. Check whether the state change is observable another
way before classifying it.

**Payload fields → schema properties.** For each field path a handler reads,
walk the mapped slug's payload schema and record one of four outcomes.
Present at `<path>`. Follow-up read via `<operationId>` with identifiers the
payload carries. Derivable from present fields, saying how and whether the
format is contractual. Absent, which goes to the gap bar. A field on the REST
component that the webhook twin lacks means a follow-up `Get…` on every
event.

## Out of domain and spec-silent

- A concept neither the spec nor `llms-full.txt` mentions (Marketplace
  billing, merge queues, Actions, Pages, Projects, Discussions, HTML probes)
  is `unknown` with an up-front question. It is never `gap`, because Origin
  has not declined it, and never `by-design-absent`, because only
  `origin-isms.md` rows earn that.
- A behavior the code depends on that the docs do not state (does an event
  fire for a draft pull request? does `updatedAt` move on a comment?) becomes an open
  question plus a hello-world step that observes it on a native repository.
  Do not settle it from GitHub's behavior.
