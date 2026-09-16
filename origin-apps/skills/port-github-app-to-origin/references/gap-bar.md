# The gap bar and the escalation card

Most differences between GitHub and Origin are not gaps. A brief that files
every difference trains the team to ignore it and buries the two or three
things Cursor actually needs to hear. Use this bar, and when in doubt, write
the row as `workaround` with an honest tradeoff and an open question rather
than as a gap card.

## Definitions

- A **difference** is any row whose parity label is not `same`.
- A **workaround** is a way to get the same outcome with the surface that
  exists today: a follow-up read, a re-keyed identifier, a path change, a
  client-side filter, a marker the app controls.
- A **gap** is a difference with **no workaround**, or a workaround whose
  tradeoff is **nontrivial**. Only gaps become escalation cards.

## What makes a tradeoff nontrivial

A workaround's tradeoff is nontrivial when at least one of these holds. Quote
the one that applies on the card.

| Tradeoff | Test |
| --- | --- |
| **Fan-out at scale** | The workaround multiplies calls per event by a factor that grows with repository or activity size (N commits × M files per push; a full list scan to find one row), and the app's event volume makes that budget-relevant. One extra bounded read per event is trivial. |
| **Correctness risk** | The workaround can produce a wrong answer, not just a slower one: identifying "my own row" by a heuristic; inferring a pull request from a SHA that several versions share; assembling a URL whose format is not contractual. |
| **Security posture** | The workaround needs a broader scope, a longer-lived token, or a user credential where an installation token should do. |
| **Product behavior visible to the team's customers** | The workaround changes what their users see or can do (no team link in a comment, no user-scoped repository picker), not just how the code is organized. |
| **Load-bearing for the port** | The capability sits on the hello-world path or on the team's stated core flow, so its tradeoff decides whether the port ships. |

If none apply, the row is `workaround`, sized honestly, with the tradeoff in
the tradeoff column and no card.

## What is never a gap

- Anything on the `origin-isms.md` list. Those rows are `by-design-absent`
  or `reshaped`, and the brief points at the idiom. Filing them wastes the
  team's and Cursor's time; the decisions are recorded.
- A field or filter the code does not actually use. Map what the code reads,
  not what the SDK exposes.
- A difference that exists only because the code uses a GitHub convenience
  (`Link` pagination, numeric IDs, `html_url`) in a place where the Origin
  convention is a mechanical substitution.
- Something the changelog says shipped or the spec already carries. Re-check
  the live spec before writing any card; the rows most likely to be stale are
  the ones you are about to escalate.
- A concept the Origin docs never mention at all (Marketplace billing, merge
  queues, Actions, Projects). That is `unknown` plus a question
  (`spec-mapping.md` § Out-of-domain surfaces); a card asks Origin to build
  something the team may not want.
- A GitHub search query. Origin has no search endpoint by design for the
  surfaces it exposes; a list operation with `sortBy`/`state`/filters plus a
  client-side predicate is the idiom. Count the fan-out honestly (a sorted
  list read that stops at a cutoff is proportional to the matches, not the
  collection), and only if that count fails the bar does it become a card
  about a *filter*, never about search.

## One pattern that does clear the bar

A state change the app reacts to that has **no event**, when the app's
purpose is to react to exactly that change and the state is otherwise
invisible until an unrelated event arrives. Reading the state off the next
event's snapshot is the workaround; it fails on correctness and
customer-visible behavior when the app is a gate (a check, a block, a
notification) and the lag is the whole failure mode. Write the card about the
event; do not write it when the app merely logs or tidies up on that change.

## The escalation card

One card per gap, in the brief's "Gaps worth raising" section, in this shape.
It is written so Cursor can act on it without a call.

```markdown
### Gap: <one line naming the capability, in Origin terms>

- **GitHub surface the app uses:** `<METHOD /path>` or `<event.action>` or `<permission>`, at `<file:line>`.
- **What the app needs from it:** <the data or effect, one sentence>.
- **Why:** <what the app does with it, one sentence>.
- **Closest Origin surface today:** `<operationId>` / `<event slug>` / none, and what it lacks.
- **Workaround considered:** <the workaround, or "none found">.
- **Tradeoff that fails the bar:** <one of the five, quoted, with the number or risk>.
- **Shape that would close it:** <a field, a filter, an event, an operation — described as a capability, not a design: "list pull requests whose head is this SHA", not a proto sketch>.
- **Blocking?** yes / no, and for which flow.
- **Spec version checked:** `<info.version>` on `<date>`.
```

Keep the card to those lines. Do not propose scope names, field names, or
route templates; Cursor owns the shape and applies design conventions the
card cannot see. Do not batch unrelated capabilities into one card.

## Where the card goes

The brief is written for the team. The cards are theirs to send, in their own
words if they prefer. Two routes exist today:

- **A shared Slack channel with Cursor**, if the team has one from working
  with Cursor on the integration. Post the card there; it reaches the people
  who own the API.
- **`hi@cursor.com`**, the feedback address the Origin documentation names.
  Put "Origin API" and the app name in the subject and paste the card.

Either way, quote the spec version the card was checked against and any
`X-Request-ID` values from failed calls (every Origin error response carries
one; the API reference asks for it when you contact Cursor). A card that
states the capability and the tradeoff cleanly is the fastest path to an
answer, including a "this is by design, here is the idiom" answer, which is a
fine outcome and belongs back in the brief as a `by-design-absent` row.

Do not send cards yourself. Write them, put them in the brief, and let the
team decide what goes out.

## Calibration examples

Illustrations of where the bar falls. Each is written as a pattern, because
the specific surface may have moved since this file was written; confirm
against the live spec before reusing the verdict.

- **A list operation lacks a filter the code relies on to find its own row**
  (for example, finding the app's own check run for a commit by name or key).
  Workaround: page the whole list and match client-side. Trivial when the
  list is small and bounded; **gap** when the list grows with activity and the
  lookup runs per event (fan-out) or when the match is heuristic
  (correctness). State which.
- **A web URL the app posts in comments is not in the payload or resource.**
  Workaround: assemble it from slug and number. Correctness risk only if the
  URL format is not contractual — check the docs; if the format is documented,
  it is `derivable`, not a gap. If it is not documented, write a card that
  asks for the URL field rather than guessing.
- **A membership roster the app uses to attribute approvals to a team** has
  no read on Origin and no workaround (identity is a TypeID; there is no
  directory). Correctness plus product behavior: **gap**, with a card that
  names the capability ("who is in group X, for a repository this
  installation can read") and leaves the oracle analysis to Cursor.
- **Push payload lacks the changed-file list.** Workaround: compare or list
  commit files on receipt. One bounded read per push is `workaround`; if the
  app fans out per commit and per file on high-volume repositories, quote the
  multiplier and let the team decide — and note that the lean payload is the
  documented design (`origin-isms.md` § Webhooks), so the card, if any, is
  about a compare endpoint's shape, not about fattening the payload.
- **The app uses GitHub Issues.** Never a card. `by-design-absent`; the
  up-front question is what the PR-scoped behavior should be.
- **The app uses commit statuses.** Never a card. `reshaped` onto check runs
  with a stable key.
