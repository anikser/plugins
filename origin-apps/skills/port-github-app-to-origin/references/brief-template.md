# Porting brief template

Contents: [Labels](#labels) (parity, size) and [Template](#template)
(provenance, §§ 1-8).

A default shape; adapt it to the app. Write one Markdown file at the
repository root (`ORIGIN-PORTING-BRIEF.md` unless the team's docs convention
says otherwise) and print its path. Cite spec `operationId`s and
`llms-full.txt` anchors. Sections 1 to 5 and 7 are for the team and may cite
their code by `file:line`. Section 6 is for Cursor and must not reveal the
team's internals; its format is the part to keep exact.

## Labels

**Parity**

| Label | Meaning |
| --- | --- |
| `same` | Same capability, same shape. A path or field rename at most. |
| `reshaped` | Same capability, different shape (pagination, identifier form, event granularity, key semantics). The code changes, the behavior does not. |
| `workaround` | Same outcome by a different route (follow-up read, client-side filter, marker). The Tradeoff column is mandatory. |
| `not-available` | Nothing in the current spec covers it (`origin-isms.md` or `#current-limitations`). Names the closest idiom and has a question in § 7; eligible for a feedback entry. |
| `gap` | No workaround, or one whose tradeoff meets a test in `gap-bar.md`. Has a feedback entry in § 6. |
| `unknown` | Discovery or the spec could not answer. Has a question in § 7. |
| `preview` (suffix) | The row touches an element badged `x-cursor-visibility: PREVIEW` (`llms-full.txt#preview`). |

**Size** (kind of change, not time)

| Size | Meaning |
| --- | --- |
| S | Adapter or client layer. A path, header, identifier, or pagination rewrite, or a re-keyed lookup. |
| M | A new code path. A follow-up read where the payload used to suffice, a handshake step, a new handler, a data-model change for a new identifier or version concept. |
| L | A product or architecture change. A flow that depended on user OAuth, a customer-visible behavior, a dependency on native repositories, an open feedback entry. |

## Template

```markdown
# Origin porting brief for <app name>

Planning document. Maps what this app uses today onto the Cursor Origin API
as published on <date>. It makes no decisions about language, framework, or
client.

## Provenance

- Origin OpenAPI `info.version`: `<value>`, fetched <timestamp>
- Docs read: <the URLs>
- Codebase: `<repo>` at `<commit>`
- Re-check `workaround` and `gap` rows against the changelog before work
  starts. They are the rows most likely to have moved.

## 1. What the app is today

One paragraph on what it does for its users, which events drive it, and what
it writes back. Then:

| Facet | Finding | Evidence |
| --- | --- | --- |
| Manifest / declared permissions | … or "none checked in; derived from calls" | `file:line` |
| Events handled | … | `file:line` |
| REST call families | <count>, in § 3 | |
| GraphQL | none / <count> documents, decomposed in § 3 | |
| Auth flow | app JWT (<alg>) → installation token; user OAuth: <yes/no, for what> | `file:line` |
| Webhook receiver | path, scheme, raw-body availability, dedupe | `file:line` |
| Git as the app | clone / push / none | `file:line` |
| Observed language and libraries | … | |
| Looked for, not found | … | |

## 2. First decision: which repositories

<What the code assumes about the repositories it acts on.> What an
installation can do on a mirrored repository is defined in
`llms-full.txt#mirrored-repositories` and `#events`. Answer question 1 before
attempting § 5.

## 3. Capability table

One row per capability the code uses today, grouped by facet (authentication,
installation and discovery, configuration, repositories and contents, pull
requests, reviews and comments, checks, webhook events, webhook receiver,
git). Include rows for calls a dependency makes on the app's behalf, marked as
such.

| Capability today (evidence) | Origin equivalent | Parity | Size | Tradeoff | Open question |
| --- | --- | --- | --- | --- | --- |
| `GET /repos/{o}/{r}/pulls/{n}` (`src/x.ts:12`) | `<operationId>` | same | S | none | none |

The Origin column names an `operationId`, a slug, a `llms-full.txt` anchor,
or `none`. `workaround` rows fill Tradeoff. `gap` rows link their feedback entry.
`not-available` rows name the closest idiom and their question. `unknown`
rows name their question.

**Scopes to request:** the union of `x-origin-scopes.scopes` across every
Origin operation above that an installation token can call, minus the scopes
`llms-full.txt#scopes` says are automatic or implied.

## 4. Webhook payload fields the code reads

| Event (today → Origin) | Field read today | Origin | How |
| --- | --- | --- | --- |
| `<event.action>` → `<slug>` | `<field path>` | present | `payload.pullRequest.head.sha` |
| `<event>` → `<slug>` | `<field path>` | follow-up read | `<operationId>`, one call per ref update |

"How" is one of five values. Present at `<path>`. Present in the envelope
(`event.type` carries the action). Follow-up read via `<operationId>`,
with the call count per event. Derivable, saying from what and whether the
format is documented. Absent, pointing at the row's label in § 3. Include
fields read only for logging.

## 5. Hello-world path

The shortest route to one real event from one native repository. The
mechanics are in `llms-full.txt#implementation-checklist` and the sections it
links; this list is the observations to make, in order. Append one step for
each spec-silent behavior the brief depends on.

1. App created, signing key registered, webhook URL and callback set.
2. Every repository event from § 3 selected in app settings.
3. Installed on an Origin-native repository; receipt verified; installation
   ID recorded.
4. Installation token minted; the repository appears in the installation's
   repositories with the mirror state § 2 expects.
5. Ping received and verified; a retried delivery is deduplicated.
6. Smallest action in § 3 performed; the expected slug and the § 4 fields
   arrive. If the ping arrived and this did not, re-check steps 2 and 3
   first.
7. Smallest write from § 3 succeeds with the scopes from the § 3 line.

## 6. Feedback for Cursor

Capabilities Origin should add, one entry per `gap` row in the `gap-bar.md`
format: use case and API gap, in Origin terms, with nothing that reveals the
team's internals. If none, write "No row met the feedback bar; the
workarounds in § 3 carry their tradeoffs."

## 7. Questions for the team

Decisions the team must make before the port, not asks of Cursor. Always the
first three, then what discovery left open.

1. Native repositories (or stable outbound mirrors), or repositories in
   another mirror state? Decides whether the app receives events and can
   write.
2. Which follow-up reads in § 4 are acceptable at your event volume, and
   which payload fields are hard requirements?
3. Which flows depend on a user credential today, and what should they do on
   Origin?
4. Does anything key approvals or reviews by commit SHA rather than pull
   request version?
5. How do you identify your own check runs, comments, and reviews today? Can
   a key or marker you control replace actor matching?
6. Do you generate clients from OpenAPI? (Read the changelog for renames.)

## 8. Out of scope

No implementation, no SDK or language choice, no time estimates. The brief is
a map. The route is the team's.
```
