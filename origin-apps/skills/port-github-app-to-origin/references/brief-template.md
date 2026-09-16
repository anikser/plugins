# Porting brief template

Write the brief as one Markdown file at the repository root
(`ORIGIN-PORTING-BRIEF.md` unless the team's docs convention says otherwise)
and print its path. Fill every section; where a section is genuinely empty,
say so in one line rather than deleting it, so the team can see it was
considered. Cite spec `operationId`s and `llms-full.txt` anchors; cite the
team's code by `file:line`.

Keep it light. A table row per capability, a line per follow-up field, a card
per gap. The team will read this in one sitting and then argue about it; give
them the shape to argue over, not prose.

## Labels used in the tables

**Parity**

| Label | Meaning |
| --- | --- |
| `same` | Same capability, same shape; a path or field rename at most. |
| `reshaped` | Same capability, different shape: pagination style, identifier form, event granularity, key semantics. The code changes, the behavior does not. |
| `workaround` | Same outcome reachable with existing surface by a different route (follow-up read, client-side filter, marker). Tradeoff column is mandatory. |
| `by-design-absent` | GitHub feature Origin deliberately does not reproduce (`origin-isms.md`). Points at the Origin idiom or says "no equivalent; decision needed". |
| `gap` | No workaround, or a workaround whose tradeoff fails the bar (`gap-bar.md`). Has a card in § Gaps worth raising. |
| `unknown` | Discovery could not determine the app's use or the spec's answer. Has an up-front question. |
| `preview` (suffix) | The Origin operation is stamped `x-cursor-visibility: PREVIEW`. Usable; shape may still move. |

**Size** — how much of the team's code changes for this row, by kind of
change, never by time:

| Size | Meaning |
| --- | --- |
| S | Contained in the adapter or client layer: a path, header, identifier, or pagination rewrite; a re-keyed lookup. |
| M | A new code path: a follow-up read where the payload used to suffice, a handshake step, a new event handler, a data-model change for a new identifier or version concept. |
| L | A product or architecture change: a flow that depended on user OAuth, a customer-visible behavior, a dependency on the customer's repositories being Origin-native, or a capability with an open gap card. |

---

## Template

```markdown
# Origin porting brief — <app name>

Planning document. Maps this GitHub App's surface onto the Cursor Origin API
as published on <date>. Contains no implementation decisions about language,
framework, or client strategy.

## Provenance

- Origin OpenAPI `info.version`: `<value>`, fetched <timestamp>
- Docs read: <the four URLs>
- Codebase: `<repo>` at `<commit>`; scanned <n> files
- Rows marked `workaround` or `gap` should be re-checked against the changelog before work starts; they are the rows most likely to have moved.

## 1. What the app is today

One paragraph in plain words: what the app does for its users, which GitHub
events drive it, what it writes back. Then the inventory:

| Facet | Finding | Evidence |
| --- | --- | --- |
| Manifest / declared permissions | … or "none checked in; permissions derived from calls" | `file:line` |
| Declared / handled events | `pull_request.opened`, … | `file:line` |
| REST call families | <count>, listed in § 3 | |
| GraphQL | none / <count> documents, decomposed in § 3 | |
| Auth flow | app JWT (<alg>) → installation token; user OAuth: <yes/no, for what> | `file:line` |
| Webhook receiver | path, verification scheme, raw-body availability, dedupe | `file:line` |
| Git as the app | clone / push / none | `file:line` |
| Observed language and libraries | … (observed only) | |
| Looked for, not found | … | |

## 2. First decision: which repositories

<State what the code assumes about the repositories it acts on.> On Origin,
an installation has full scopes only on Origin-native repositories and
stable outbound mirrors; repositories mirrored from GitHub are read-only to
apps and do not deliver push events. **Question 1 below must be answered
before the hello-world path is attempted.**

## 3. Capability table

One row per GitHub capability the code uses. Group rows by facet
(authentication, installation & discovery, repositories & contents, pull
requests, reviews & comments, checks, webhooks, git). Follow-up fields go in
§ 4, not here.

| GitHub thing (evidence) | Origin equivalent | Parity | Size | Tradeoff | Open question |
| --- | --- | --- | --- | --- | --- |
| `GET /repos/{o}/{r}/pulls/{n}` (`src/x.ts:12`) | `OriginService_GetPullRequest` | same | S | — | — |
| … | … | … | … | … | … |

Rules for the table: the Origin column names an `operationId`, an event
slug, a `llms-full.txt` anchor, or `none`; `workaround` rows always fill
Tradeoff; `gap` rows link their card; `by-design-absent` rows name the idiom
in the Tradeoff column; `unknown` rows name their question. Group rows by
facet with a bold header row (Authentication · Installation & discovery ·
Configuration · Repositories & contents · Pull requests · Reviews & comments
· Checks · Webhooks: events · Webhooks: receiver · Git), and include rows
for calls a dependency makes on the app's behalf, marked as such.

**Scopes to request** (one line under the table): the union of
`x-origin-scopes.scopes` across every Origin operation named above that an
installation token can call, minus scopes that are ambient or implied
(`write` implies `read`; `repository:metadata:read` is automatic). This is
what the install URL's `scope` parameter carries, so the team can read it
straight off the brief.

## 4. Webhook payload fields the code reads

For each mapped event, the fields the handlers dereference.

| Event (GitHub → Origin) | GitHub field | Origin | How |
| --- | --- | --- | --- |
| `pull_request.synchronize` → `pull_request.head_ref.pushed` | `pull_request.head.sha` | present | `payload.pullRequest.head.sha` |
| `push` → `repository.pushed` | `commits[].added` | follow-up read | `OriginService_ListComparisonFiles` on `refUpdates[].before..after` — one call per ref update |
| … | `repository.html_url` | derivable / absent | … |

"How" is one of: present at `<path>`; present in envelope (`event.type` for
GitHub's `action`); follow-up read via `<operationId>` (state the call count
per event); derivable (say from what, and whether the format is documented);
absent (→ § 3's label for that row: `by-design-absent`, `unknown`, or a § 6
card). Include fields the code reads only for logging; they are the ones
teams forget until a dashboard breaks.

## 5. Hello-world path

The shortest route to one real event from one native repository. Each step
is something to verify, not code to write. Link each to `llms-full.txt`.
Append one step per spec-silent behavior the brief depends on (see the
questions), stated as the observation to make.

1. **Create the app** in the target namespace's app settings; register the
   Ed25519 public key only; set the webhook URL and the callback URI.
2. **Subscribe to events.** Installation lifecycle events arrive regardless;
   select every repository event from § 3 explicitly. An unselected event is
   silence, not an error.
3. **Install** on an Origin-native repository (or a stable outbound mirror).
   Verify the installation receipt (`kid` → JWKS, `alg`, `typ`, `iss`, `aud`,
   `exp`, `state`); read the installation ID from `sub`. Never send the
   receipt as a Bearer token.
4. **Mint** an app JWT (EdDSA, ~5 min) and exchange it for an installation
   token; call `/installation/repos` and confirm the repository is listed
   and its `mirror` state is what § 2 expects.
5. **Ping** the receiver and verify `v1ed` over the raw body against the
   JWKS; check timestamp skew handling and `webhook-id` dedupe.
6. **First real event**: perform the smallest action in § 3 on the native
   repository (open a PR, push a branch) and confirm the delivery arrives
   with the expected slug and the payload fields from § 4. If the ping
   arrived and this did not, re-check steps 2 and 3 before anything else.
7. **First write back** (if the app writes): the smallest write from § 3
   (a check run with a stable `key`, a PR comment), confirming the scope
   from `x-origin-scopes` is in the installation grant.

## 6. Gaps worth raising

Zero or more cards in the `gap-bar.md` shape. If zero, say: "No row failed
the gap bar; the workarounds in § 3 carry their tradeoffs." Do not pad.

## 7. Questions for the team

Pruned to what discovery left open, plus anything specific found. Always
starts with the first three.

1. Will the app run against Origin-native repositories (or stable outbound
   mirrors), or against repositories mirrored from GitHub? (Decides whether
   the app receives events and can write at all.)
2. Which of the follow-up reads in § 4 are acceptable at your event volume,
   and which payload fields are hard requirements?
3. Which flows depend on a user credential today (user OAuth, install-by-user
   pickers, acting on behalf of a user), and what should they do on Origin?
4. Does anything key approvals or reviews by commit SHA rather than by pull
   request version?
5. Do you generate clients from OpenAPI? (Then read the changelog for schema
   renames and check reserved names in your language.)
6. How do you identify your own check runs / comments / reviews today, and
   can a key or marker you control replace actor matching?
7. What is your first success metric: ping received, first real event, or
   first write back on a native repository?
8. Anything marked `unknown` in § 1 or § 3.

## 8. Out of scope for this brief

No implementation, no SDK or language choice, no effort estimates in time.
The brief is a map; the route is the team's.
```
