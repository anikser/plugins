# Porting brief template

One Markdown file at the repository root (`ORIGIN-PORTING-BRIEF.md` unless the
team's docs convention says otherwise); print its path. Fill every section; an
empty section says so in one line rather than disappearing. Cite spec
`operationId`s and `llms-full.txt` anchors; cite the team's code by
`file:line`. A table row per capability, a line per follow-up field, a card
per gap; the team will argue over it in one sitting.

## Labels

**Parity**

| Label | Meaning |
| --- | --- |
| `same` | Same capability, same shape; a path or field rename at most. |
| `reshaped` | Same capability, different shape (pagination, identifier form, event granularity, key semantics). Code changes, behavior does not. |
| `workaround` | Same outcome by a different route (follow-up read, client-side filter, marker). Tradeoff column mandatory. |
| `by-design-absent` | Origin deliberately does not reproduce it (`origin-isms.md`). Names the idiom or "no equivalent; decision needed". |
| `gap` | No workaround, or one that fails `gap-bar.md`. Has a card in § 6. |
| `unknown` | Discovery or the spec could not answer. Has a question in § 7. |
| `preview` (suffix) | Origin operation is `x-cursor-visibility: PREVIEW`. Usable; shape may move. |

**Size** (kind of change, never time)

| Size | Meaning |
| --- | --- |
| S | Adapter or client layer: path, header, identifier, or pagination rewrite; re-keyed lookup. |
| M | New code path: a follow-up read where the payload sufficed, a handshake step, a new handler, a data-model change for a new identifier or version concept. |
| L | Product or architecture change: a flow that depended on user OAuth, a customer-visible behavior, a dependency on native repositories, an open gap card. |

## Template

```markdown
# Origin porting brief — <app name>

Planning document. Maps this GitHub App's surface onto the Cursor Origin API
as published on <date>. No decisions about language, framework, or client.

## Provenance

- Origin OpenAPI `info.version`: `<value>`, fetched <timestamp>
- Docs read: <the URLs>
- Codebase: `<repo>` at `<commit>`
- Re-check `workaround` and `gap` rows against the changelog before work
  starts; they move most.

## 1. What the app is today

One paragraph: what it does for its users, which events drive it, what it
writes back. Then:

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

<What the code assumes about the repositories it acts on.> Apps have full
scopes only on Origin-native repositories and stable outbound mirrors;
repositories mirrored from GitHub are read-only to apps and deliver no push
events. **Question 1 must be answered before § 5 is attempted.**

## 3. Capability table

One row per GitHub capability the code uses, grouped by facet with a bold
header row (Authentication · Installation & discovery · Configuration ·
Repositories & contents · Pull requests · Reviews & comments · Checks ·
Webhooks: events · Webhooks: receiver · Git). Include rows for calls a
dependency makes on the app's behalf, marked as such.

| GitHub thing (evidence) | Origin equivalent | Parity | Size | Tradeoff | Open question |
| --- | --- | --- | --- | --- | --- |
| `GET /repos/{o}/{r}/pulls/{n}` (`src/x.ts:12`) | `<operationId>` | same | S | — | — |

The Origin column names an `operationId`, a slug, a `llms-full.txt` anchor,
or `none`. `workaround` rows fill Tradeoff; `gap` rows link their card;
`by-design-absent` rows name the idiom; `unknown` rows name their question.

**Scopes to request:** the union of `x-origin-scopes.scopes` across every
Origin operation above that an installation token can call, minus ambient
and implied scopes (`write` implies `read`; `repository:metadata:read` is
automatic). This is what the install URL's `scope` parameter carries.

## 4. Webhook payload fields the code reads

| Event (GitHub → Origin) | GitHub field | Origin | How |
| --- | --- | --- | --- |
| `pull_request.synchronize` → `<slug>` | `pull_request.head.sha` | present | `payload.pullRequest.head.sha` |
| `push` → `<slug>` | `commits[].added` | follow-up read | `<operationId>`, one call per ref update |

"How" is one of: present at `<path>`; present in envelope (`event.type` for
GitHub's `action`); follow-up read via `<operationId>` with the call count
per event; derivable (from what; is the format documented); absent (→ § 3's
label). Include fields read only for logging.

## 5. Hello-world path

Shortest route to one real event from one native repository. Each step is a
verification, linked to `llms-full.txt`; append one step per spec-silent
behavior the brief depends on, stated as the observation to make.

1. Create the app; register the Ed25519 public key; set webhook URL and
   callback.
2. Select every repository event from § 3 in app settings.
3. Install on an Origin-native repository; verify the receipt JWT and read
   the installation ID from `sub`.
4. Mint an app JWT, exchange for an installation token, confirm the
   repository is listed and its mirror state matches § 2.
5. Verify the ping (`v1ed` over the raw body, timestamp skew, `deliveryId`
   dedupe).
6. Perform the smallest action in § 3 and confirm the slug and the § 4
   fields arrive. Ping but no event: re-check steps 2 and 3 first.
7. Smallest write from § 3 (check run with a stable `key`, PR comment),
   confirming its scope is in the grant.

## 6. Gaps worth raising

Zero or more cards in the `gap-bar.md` shape. If zero: "No row failed the gap
bar; the workarounds in § 3 carry their tradeoffs." Do not pad.

## 7. Questions for the team

Always the first three; then what discovery left open.

1. Native repositories (or stable outbound mirrors), or repositories mirrored
   from GitHub? Decides whether the app receives events and can write.
2. Which follow-up reads in § 4 are acceptable at your event volume, and
   which payload fields are hard requirements?
3. Which flows depend on a user credential today, and what should they do on
   Origin?
4. Does anything key approvals or reviews by commit SHA rather than PR
   version?
5. How do you identify your own check runs / comments / reviews today; can a
   key or marker you control replace actor matching?
6. Do you generate clients from OpenAPI? (Read the changelog for renames.)

## 8. Out of scope

No implementation, no SDK or language choice, no time estimates. The brief is
a map; the route is the team's.
```
