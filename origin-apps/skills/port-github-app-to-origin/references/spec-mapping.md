# Reading the Origin spec and matching GitHub surface to it

Every mapping in the brief is derived from the fetched `openapi.yaml`, not
from a table here. Build the index once; every later step looks things up in
it.

## Extensions the spec carries

| Extension | Where | Meaning |
| --- | --- | --- |
| `x-origin-scopes` | every operation | `scopes` required; `tokenTypes` accepted (`app`, `installation`, `user`); `ambient: true` means nothing to request. |
| `x-origin-webhook-events` | payload schemas | The slugs that deliver this payload shape. A schema carrying it is a webhook family; these slugs are the only authoritative event list. |
| `x-origin-webhook-resource` | some payload schemas | The REST component the payload embeds. When absent, infer from `$ref`s; pushes, deletions, and reviewer requests are event-native with no REST twin. |
| `x-cursor-visibility: PREVIEW` | some operations | Usable, shape may move. Carry the badge into the brief as a `preview` suffix. |

## Build the index

1. **Operations**: `operationId`, method, path, `x-origin-scopes`,
   visibility, parameter names, request top-level fields, response component.
2. **Webhook events**: slug → schema → properties and `$ref`s (or the
   `x-origin-webhook-resource` target). From `llms-full.txt` § Webhooks,
   which slugs are app-lifecycle (always delivered) versus repository events
   (must be selected).
3. **Scopes**: union of every `scopes` value, annotated with the operations
   that need it; separate installation-requestable scopes from ambient and
   user-only ones (the latter tell you which GitHub flows have no app-side
   equivalent by construction).
4. **Resources**: component schemas returned by `Get…`/`List…`, with field
   names, for "does the Origin object carry this field".

`scripts/index-origin-spec.py openapi.yaml [ops|events|scopes|schema <Name>]`
prints all four.

## Matching

Match in this order; stop at the first rule that yields a *confirmed*
counterpart. Confirmed means you read the Origin operation's description and
parameters and it answers the same question. A name match is a candidate,
never a result.

**REST calls**

1. Normalize the GitHub path to the same shape under `/v1/origin`
   (`{owner}/{repo}` → `{ownerSlug}/{repoName}`, `{pull_number}` →
   `{pullNumber}`; custom verbs are `:verb` suffixes such as
   `…/contents:batchGet`).
2. Re-home GitHub's issue-flavored PR calls: `/issues/{n}/comments` and
   `/issues/{n}/labels` used *on a pull request* live under `/pulls/{n}/…`.
   Path change, not a gap. Used on real issues: `origin-isms.md`.
3. Re-home `/app`, `/app/installations`, access-token minting, and
   `/installation/repositories` under `/v1/origin/app…` and
   `/v1/origin/installation/repos`; confirm `tokenTypes`. `/user`,
   `/user/installations`, `/orgs/…`, `/search/…`, `/repositories/{id}` have
   no path counterpart: consult `origin-isms.md` before labeling.
4. Compare parameters, not just paths. A matching path missing a filter the
   code depends on is `workaround` or `gap`, not `same`.
5. Compare response fields the code reads. Each missing field gets its own
   line: follow-up call, derivable, or absent. GitHub inlines convenience
   data (web URLs, nested profiles, counts) that Origin does not.

**GraphQL.** No endpoint. Decompose each document into the REST reads and
writes it stands for, map those, and record the fan-out as the row's
tradeoff.

**Permissions → scopes.** Do not translate the manifest noun-for-noun. Find
the operations the code calls and take the union of *their*
`x-origin-scopes.scopes`. GitHub permissions with no Origin noun
(`statuses`, `issues`, `members`, `organization_*`, `pages`, `actions`,
`workflows`, `deployments`) go through `origin-isms.md` first.

**Events → slugs.** Each GitHub `event` + `action` pair becomes a candidate
slug (`pull_request` + `synchronize` → `pull_request.head_ref.pushed`);
confirm it exists in the webhook index. A candidate that does not exist is
not an event on Origin; check whether the state change is observable another
way before classifying.

**Payload fields → schema properties.** For each field path a handler reads,
walk the mapped slug's payload schema and record one of: **present** at
`<path>`; **follow-up read** via `<operationId>` with identifiers the payload
carries; **derivable** from present fields (say how, and whether the format
is contractual); **absent** (goes to the gap bar). A field on the REST
component that the webhook twin lacks is a follow-up `Get…` on every event.

## Out of domain and spec-silent

- A concept neither the spec nor `llms-full.txt` mentions (Marketplace
  billing, merge queues, Actions, Pages, Projects, Discussions, HTML probes)
  is `unknown` with an up-front question. Never `gap` (Origin has not
  declined it) and never `by-design-absent` (only `origin-isms.md` rows earn
  that).
- A behavior the code depends on that the docs do not state (does an event
  fire for a draft PR? does `updatedAt` move on a comment?) is an open
  question plus a hello-world step that observes it on a native repository.
  Do not resolve it from GitHub's behavior.
