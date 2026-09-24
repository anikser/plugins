# Origin-isms: GitHub features that map differently on Origin

Check here before labeling anything `gap`. Each row names the label to use
and where the Origin answer lives today (an anchor in `llms-full.txt` unless
noted). `reshaped` rows have a documented path, so they get a question if
the team wants the GitHub shape back rather than a card. `not-available`
rows get a question, and a card if they meet the gap bar.
Read the source; do not copy this table into the brief.

| GitHub call, event, or permission | Label | Where the Origin answer lives |
| --- | --- | --- |
| Writes or `push` events on a repository mirrored from GitHub | `reshaped` | Read-only until the mirror becomes a stable outbound mirror (`#mirrored-repositories`); pushes are not delivered for GitHub-sourced mirrors (`#events`). Transitioning is a user-credential operation. First question of every brief. |
| Install callback query parameters (`installation_id`, `setup_action`) | `reshaped` | `#installation-receipt` |
| RS256 app JWT | `reshaped` | `#app-jwt` |
| Long-lived installation tokens | `reshaped` | `#installation-access-token` |
| User OAuth, `/user`, `/user/installations`, install-by-user picker | `not-available` | No user-credential flow for apps in the current spec. Repository discovery is through the installation; namespace-wide listing is under `#current-limitations`. Ask what the flow should do. |
| Permissions `<noun>: read\|write` | `reshaped` | `#scopes`; `x-origin-scopes` per operation |
| Numeric IDs, `/repositories/{id}` | `reshaped` | `#ids`, `#repository-paths` |
| `Link` / `page` / `per_page` pagination, total counts | `reshaped` | `#pagination` |
| GraphQL | `not-available` | No GraphQL endpoint in the current spec. Decompose into REST calls and count the fan-out; a decomposition that fails the gap bar earns a card about that read. |
| Commit statuses (`statuses` permission, `POST /statuses/{sha}`) | `reshaped` | `#check-runs` (check runs with a stable `key`) |
| Issues (`issues` permission, `issues.*` events, `/issues/{n}` not on a pull request) | `not-available` | No Issues endpoints or events in the current spec. Pull request comments, threads, reviews, and labels cover the pull-request half. Ask what the team needs for the rest; an issue-driven app may earn a card. |
| `/issues/{n}/comments`, `/issues/{n}/labels` used on a pull request | `reshaped` | Pull requests endpoint reference; same calls under `/pulls/{n}/…` |
| Repository webhook CRUD (`/repos/…/hooks`) | `reshaped` | Subscriptions are set per app through Create App / Update App `events` (`#events`). |
| App-manifest conversion | `reshaped` | App creation form or `CreateApp` (`#installation`, endpoint reference) |
| OAuth-app token mints | `not-available` | Nothing in the current spec. Ask what the flow was for. |
| Git Data API commit and ref writes | `reshaped` | Create Commit From Files, Create Git Ref (Git data endpoint reference); `#git-https-authentication` for pushes |
| Git Data API arbitrary blob or tree writes | `not-available` | Not in the current spec. Ask whether commit-from-files or a push covers the use. |
| Standalone review-thread objects | `reshaped` | A thread comes from its first diff-anchored comment (Pull requests endpoint reference); thread listing is under `#current-limitations`. |
| User, email, team, and member lookups | `not-available` | No directory reads in the current spec. Reviewer identifiers resolve by public id, user email, or group slug; `handle` is present when the profile is public (`#resource-references`). |
| Single `pull_request` event with an `action` field, `previous_attributes` | `reshaped` | `#events`, `#event-payloads` |
| `x-github-*` headers, HMAC `x-hub-signature-256` | `reshaped` | `#headers`, `#signature-verification` |
| Payload inlines (changed files on push, before-SHA, `html_url`, `sender` profile) | `reshaped` | `#resource-references`; the push commit list is under `#current-limitations` and may change. Name the follow-up call per field and count the fan-out. |
| All events delivered after app creation | `reshaped` | `#events` |
| Reviews keyed by `commit_id` | `reshaped` | `pullRequestVersion` on the review schema |
| Finding own check runs or comments by actor | `reshaped` | `#check-runs` (`key`); comments and reviews by a marker the app controls |
| Requested-reviewer team pages, `created_via` | `not-available` | Groups exist and resolve by slug; there is no group membership read in the current spec. |

A feature that is not on this list and that the Origin docs do not mention
is `unknown` with a question.
