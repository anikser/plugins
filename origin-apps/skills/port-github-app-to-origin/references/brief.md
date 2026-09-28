# The brief, the feedback, and the crib

## The brief

One Markdown file at the repository root (`ORIGIN-PORTING-BRIEF.md` unless
the team's convention says otherwise); print its path. Budget about 800
words for a small app and about 2,000 for a large one; parts with nothing to
say collapse or disappear. Choose table shapes to fit the app. A good brief:

- leads with a summary: the verdict (ports as is, ports with workarounds,
  blocked on X), the question that decides the rest (usually native or
  mirror), and whether there is feedback for Cursor and if any of it blocks;
- lists only the capabilities that do not map straight across, each with
  the Origin operation, slug, or docs section it maps to or a note that
  nothing does, and closes the list with one line naming the rest
  ("maps directly: 14 operations, covered by the scopes line"); shows a
  payload field only when it is absent or needs a follow-up read; ends with
  the scopes to request;
- gives an app-specific first-run path when it helps (events to select, the
  mirror check, the first event and what it carries, the first write); skips
  generic setup, which "Implementation checklist" covers;
- notes what drives the size of the port and how to roll it out (dual-run
  or cutover), without time estimates;
- asks only what the team must decide, never restating a row;
- ends with two lines of provenance (spec `info.version` and fetch time;
  codebase and commit) and then Feedback for Cursor, last and unnumbered.

Evidence for every app claim (`file:line`, or "from `<dependency>`"); every
Origin claim resolved against the fetched docs. If you want compact marks:
`maps` (a documented path exists), `workaround` (say the tradeoff),
`not-available` (nothing in the current spec; carries a question), `gap`
(produces a feedback entry).

## Feedback for Cursor

Cursor wants to hear what the team needs. Raise anything that blocks the
team's core flow, costs them correctness, security, or scale, or that they
would like Origin to do. The bar sorts items into feedback (a capability
Origin should add) and questions (decisions the team must make); it does not
decide whether to speak up.

A workaround reaches the same outcome by another route (a follow-up read, a
re-keyed identifier, a path change, a client-side filter, a marker the app
controls) and is often the right answer. It becomes a gap, and a feedback
entry, when its tradeoff is one of: fan-out that grows with repository or
activity size at the app's volume; a possibly wrong answer (heuristic own-row
matching, a pull request inferred from a SHA several versions share, a URL
whose format is not contractual); a broader scope, longer-lived token, or
user credential where an installation token should do; a change to what the
team's users see or can do; or a capability on the hello-world path or the
team's core flow. A state change the app exists to react to, with no event
and no other way to observe it, meets the bar. Something the docs never
mention is not available today and gets a question; it becomes feedback
only if it blocks the core flow.

Not feedback, only a question or a note: a field or filter the code does not
use; a convention difference with a mechanical substitute; a documented
design choice such as token lifetime or no GraphQL.

One entry per gap, in Origin terms, with nothing that reveals the team's
internals. When there is at least one, also write the section to
`ORIGIN-FEEDBACK.md` beside the brief; when there is none, no file and one
line saying so. The file carries no license header, repository name,
product name, or mention of another forge. A contradiction between the docs
and observed behavior goes in a short "Docs questions for Cursor" list at
the end of the feedback, not in the questions for the team. A suggested
shape:

```markdown
### Feedback: <capability, in Origin terms>
- **Use case:** the app needs to <do what, for whom>, <how often or at what volume>.
- **Origin today:** <what is missing or costly; cite the closest operationId, slug, or section, or "no operation">.
- **Workaround considered:** <the route and the tradeoff that makes it insufficient, or "none found">.
- **Blocking?** yes / no, for which flow.
- **Spec version checked:** <info.version>, <date>.
```

Describe the capability rather than proposing scope, field, or route names.
The team sends the feedback, not you; before they do, they strip anything
that reveals their internals.

## Crib: where GitHub habits land on Origin

Check before calling anything a gap; confirm each in the fetched docs.

Documented path exists: install callback params → "Installation receipt";
RS256 app JWT → "App JWT"; long-lived installation tokens → "Installation
access token"; permissions → "Scopes" and `x-origin-scopes`; numeric IDs and
`/repositories/{id}` → "IDs", "Repository paths"; `Link` pagination and
totals → "Pagination"; commit statuses → check runs with a stable `key`
("Check runs"); `/issues/{n}/comments` and `/issues/{n}/labels` on a pull
request → the pull request endpoints; repository webhook CRUD → per-app
`events` on Create App / Update App; a single `pull_request` event with an
`action` field → one slug per action ("Events"); `x-github-*` headers and
HMAC → "Headers", "Signature verification"; inlined payload data (changed
files, before-SHA, URLs, profiles) → follow-up reads ("Resource references",
"Current limitations"); reviews keyed by commit SHA → `pullRequestVersion`;
finding own rows by actor → check-run `key`, or a marker the app controls;
writes on a repository mirrored from GitHub → metadata and contents reads
only, until it is a stable outbound mirror, and merging and default-branch
changes stay native-only ("Mirrored repositories"); user sign-in and acting
as a user → "Acting on behalf of users" (user confirmation receipt,
installation user tokens).

Not available in the current spec (question, and feedback if it blocks the
core flow): GraphQL (decompose); Issues (pull request comments, threads,
reviews, and labels cover the pull-request half); OAuth-app token mints;
arbitrary blob or tree writes (commit-from-files and pushes exist); user,
email, team, and member directory reads (reviewer identifiers resolve by
public id, email, or group slug); group membership and effective-permission
reads. For the last two, the workaround to name is a user token capped to a
repository and scopes: minting it returns `403` unless the user holds that
permission, so it doubles as a permission probe.

Crib rows go stale; the fetched docs win.
