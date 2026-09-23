# The gap bar and the escalation card

Most differences are not gaps. A brief that files every difference buries
the two or three things Cursor needs to hear. When in doubt, write the row as
`workaround` with an honest tradeoff and an open question, not as a card.

- A **difference** is any row whose parity label is not `same`.
- A **workaround** reaches the same outcome with today's surface: a follow-up
  read, a re-keyed identifier, a path change, a client-side filter, a marker
  the app controls.
- A **gap** is a difference with no workaround, or a workaround whose tradeoff
  is nontrivial. Only gaps become cards.

## Nontrivial tradeoff

At least one must hold; quote it on the card.

| Tradeoff | Test |
| --- | --- |
| **Fan-out at scale** | Calls per event multiply by a factor that grows with repository or activity size (N commits × M files; a full list scan to find one row) and the app's volume makes that budget-relevant. One bounded extra read per event is trivial. |
| **Correctness risk** | The workaround can be wrong, not just slower: heuristic "my own row" matching, inferring a PR from a SHA several versions share, assembling a URL whose format is not contractual. |
| **Security posture** | Needs a broader scope, a longer-lived token, or a user credential where an installation token should do. |
| **Customer-visible behavior** | Changes what the team's users see or can do, not how the code is organized. |
| **Load-bearing** | Sits on the hello-world path or the team's stated core flow. |

## Never a gap

- Anything in `origin-isms.md`.
- A field or filter the code does not actually use.
- A GitHub convenience (`Link` pagination, numeric IDs, `html_url`) where the
  Origin convention is a mechanical substitution.
- Something the changelog says shipped or the spec already carries. Re-check
  the live spec before writing any card.
- A concept the Origin docs never mention (Marketplace billing, merge queues,
  Actions, Projects): `unknown` plus a question.
- A GitHub Search query. The idiom is a list operation with its filters plus
  a client-side predicate; a sorted list read that stops at a cutoff is
  proportional to the matches, not the collection. Only if that count fails
  the bar does it become a card about a *filter*, never about search.

## One pattern that does clear the bar

A state change the app reacts to that has **no event**, when reacting to
exactly that change is the app's purpose and the state is invisible until an
unrelated event arrives. Reading it off the next snapshot fails on
correctness and customer-visible behavior when the app is a gate (a check, a
block, a notification). Write the card about the event; not when the app
merely logs or tidies up on that change.

## The card

One per gap, in the brief's "Gaps worth raising" section, written so Cursor
can act without a call:

```markdown
### Gap: <capability, in Origin terms>

- **GitHub surface the app uses:** `<METHOD /path>` / `<event.action>` / `<permission>`, at `<file:line>`.
- **What the app needs from it:** <data or effect, one sentence>.
- **Why:** <what the app does with it, one sentence>.
- **Closest Origin surface today:** `<operationId>` / `<slug>` / none, and what it lacks.
- **Workaround considered:** <it, or "none found">.
- **Tradeoff that fails the bar:** <one of the five, with the number or risk>.
- **Shape that would close it:** <a capability, not a design: "list pull requests whose head is this SHA", not a route or field name>.
- **Blocking?** yes / no, for which flow.
- **Spec version checked:** `<info.version>` on `<date>`.
```

Do not propose scope, field, or route names; Cursor owns the shape. Do not
batch unrelated capabilities. Do not send cards yourself; the team decides
what goes out (their shared Slack channel with Cursor, or `hi@cursor.com`
with "Origin API" and the app name in the subject), quoting the spec version
and any `X-Request-ID` from failed calls. "This is by design, here is the
idiom" is a fine answer and goes back into the brief as `by-design-absent`.
