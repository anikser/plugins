# The gap bar and the escalation card

Cursor wants to hear what the team needs from Origin. Raise anything that
blocks the team's core flow, costs them correctness, security, or scale, or
that they would simply like Origin to do. The bar below decides whether an
item is a card or a question, not whether to speak up. Its other job is
ordering: put the asks that block the port ahead of the ones that are
conveniences, so the important ones are read first. When a difference has a
workaround, writing the row as `workaround` with its tradeoff and a question
is often the right answer; a card adds the tradeoff analysis Cursor needs to
prioritize it.

- A difference is any row whose parity label is not `same`.
- A workaround reaches the same outcome with the current API by another route. A
  follow-up read, a re-keyed identifier, a path change, a client-side filter,
  a marker the app controls.
- A gap is a difference with no workaround, or a workaround whose tradeoff
  meets one of the five tests below. Gaps become cards; everything else the
  team wants to raise becomes a question in § 7.

## Nontrivial tradeoff

At least one should hold for a card. Quote it on the card.

| Tradeoff | Test |
| --- | --- |
| Fan-out at scale | Calls per event multiply by a factor that grows with repository or activity size (N commits × M files, or a full list scan to find one row), and the app's volume makes that budget-relevant. One bounded extra read per event is a workaround. |
| Correctness risk | The workaround can return a wrong answer, not only a slower one. Heuristic "my own row" matching. Inferring a pull request from a SHA several versions share. Assembling a URL whose format is not contractual. |
| Security posture | The workaround needs a broader scope, a longer-lived token, or a user credential where an installation token should do. |
| Customer-visible behavior | The workaround changes what the team's users see or can do, not how the code is organized. |
| Load-bearing | The capability sits on the hello-world path or the team's stated core flow. |

## Usually a workaround or a question, not a card

- Anything `origin-isms.md` labels `reshaped`: a documented path exists.
- A field or filter the code does not use.
- A GitHub convenience (`Link` pagination, numeric IDs, `html_url`) where the
  Origin convention is a mechanical substitution.
- Anything the changelog says shipped or the spec already carries. Re-read the
  live spec before writing any card.
- A concept the Origin docs do not mention. That is `not-available` or
  `unknown` with a question; the team should still ask if they need it.
- A GitHub Search query, when the spec has no search operation for that
  resource. The idiom is a list operation with its filters plus a client-side
  predicate. A sorted list read that stops at a cutoff costs proportional to
  the matches, not the collection. If that count meets the bar, the card is
  usually about a filter rather than search.

## One pattern that does meet the bar

A state change the app reacts to that has no event, when reacting to exactly
that change is the app's purpose and the state is invisible until an
unrelated event arrives. Reading it off the next snapshot fails on correctness
and customer-visible behavior when the app is a gate (a check, a block, a
notification). Write the card about the event. When the app only logs or
tidies up on that change, a question is enough.

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
- **Tradeoff that meets the bar:** <one of the five, with the number or risk>.
- **Shape that would close it:** <a capability, not a design. "List pull requests whose head is this SHA", not a route or field name.>
- **Blocking?** yes / no, for which flow.
- **Spec version checked:** `<info.version>` on `<date>`.
```

Describe the capability rather than proposing scope, field, or route names;
that leaves Cursor free to fit it to the API's conventions. One capability
per card. Do not send cards yourself: the team decides what goes out, and
they are encouraged to send both the cards and the § 7 questions to Cursor
through whatever contact route they have, quoting the spec version and any
request ID from failed calls (`llms-full.txt#errors`). A reply of "here is
the idiom" or "not planned" is useful too; record it in the brief with the
label it earns.
