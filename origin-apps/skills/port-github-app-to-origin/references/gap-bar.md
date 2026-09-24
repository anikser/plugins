# The gap bar and the escalation card

Most differences are not gaps. A brief that files every difference buries the
two or three things Cursor needs to hear. When in doubt, write the row as
`workaround` with the tradeoff and an open question, not as a card.

- A difference is any row whose parity label is not `same`.
- A workaround reaches the same outcome with the current API by another route. A
  follow-up read, a re-keyed identifier, a path change, a client-side filter,
  a marker the app controls.
- A gap is a difference with no workaround, or a workaround whose tradeoff
  fails one of the five tests below. Only gaps become cards.

## Nontrivial tradeoff

At least one must hold. Quote it on the card.

| Tradeoff | Test |
| --- | --- |
| Fan-out at scale | Calls per event multiply by a factor that grows with repository or activity size (N commits × M files, or a full list scan to find one row), and the app's volume makes that budget-relevant. One bounded extra read per event is trivial. |
| Correctness risk | The workaround can return a wrong answer, not only a slower one. Heuristic "my own row" matching. Inferring a pull request from a SHA several versions share. Assembling a URL whose format is not contractual. |
| Security posture | The workaround needs a broader scope, a longer-lived token, or a user credential where an installation token should do. |
| Customer-visible behavior | The workaround changes what the team's users see or can do, not how the code is organized. |
| Load-bearing | The capability sits on the hello-world path or the team's stated core flow. |

## Never a gap

- Anything in `origin-isms.md`.
- A field or filter the code does not use.
- A GitHub convenience (`Link` pagination, numeric IDs, `html_url`) where the
  Origin convention is a mechanical substitution.
- Anything the changelog says shipped or the spec already carries. Re-read the
  live spec before writing any card.
- A concept the Origin docs never mention (Marketplace billing, merge queues,
  Actions, Projects). That is `unknown` plus a question.
- A GitHub Search query. The idiom is a list operation with its filters plus a
  client-side predicate. A sorted list read that stops at a cutoff costs
  proportional to the matches, not the collection. If that count fails the
  bar, the card is about a filter, never about search.

## One pattern that does clear the bar

A state change the app reacts to that has no event, when reacting to exactly
that change is the app's purpose and the state is invisible until an
unrelated event arrives. Reading it off the next snapshot fails on correctness
and customer-visible behavior when the app is a gate (a check, a block, a
notification). Write the card about the event. Do not write it when the app
only logs or tidies up on that change.

## The card

One per gap, in the brief's "Gaps worth raising" section. Write it so Cursor
can act without a call.

```markdown
### Gap: <capability, in Origin terms>

- **GitHub call, event, or permission:** `<METHOD /path>` / `<event.action>` / `<permission>`, at `<file:line>`.
- **What the app needs from it:** <data or effect, one sentence>.
- **Why:** <what the app does with it, one sentence>.
- **Closest Origin operation:** `<operationId>` / `<slug>` / none, and what it lacks.
- **Workaround considered:** <it, or "none found">.
- **Tradeoff that fails the bar:** <one of the five, with the number or risk>.
- **Shape that would close it:** <a capability, not a design. "List pull requests whose head is this SHA", not a route or field name.>
- **Blocking?** yes / no, for which flow.
- **Spec version checked:** `<info.version>` on `<date>`.
```

Do not propose scope, field, or route names. Cursor owns the shape. Do not
batch unrelated capabilities. Do not send cards yourself. The team decides
what goes out, through their shared Slack channel with Cursor or to
`hi@cursor.com` with "Origin API" and the app name in the subject, quoting the
spec version and any `X-Request-ID` from failed calls. "This is by design,
here is the idiom" is a fine answer. It goes back into the brief as
`by-design-absent`.
