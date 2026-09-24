# Origin-isms: GitHub features Origin departs from on purpose

Check here before labeling anything `gap`. A row below is `by-design-absent`
or `reshaped`. The brief points at the idiom and never files a card. The
third column is the `llms-full.txt` anchor where the Origin answer lives.
Read the source; do not copy this table into the brief.

| GitHub call, event, or permission | Label | Where the Origin answer lives |
| --- | --- | --- |
| Writes or `push` events on a repository mirrored from GitHub | `by-design-absent` | `#mirrored-repositories`, `#events`. First question of every brief. |
| Install callback query parameters (`installation_id`, `setup_action`) | `reshaped` | `#installation-receipt` |
| RS256 app JWT | `reshaped` | `#app-jwt` |
| Long-lived installation tokens | `reshaped` | `#installation-access-token` |
| User OAuth, `/user`, `/user/installations`, install-by-user picker | `by-design-absent` | `#coming-from-github`; `#scopes` (user-credential operations). Ask what the flow should do. |
| Permissions `<noun>: read\|write` | `reshaped` | `#scopes`; `x-origin-scopes` per operation |
| Numeric IDs, `/repositories/{id}` | `reshaped` | `#ids`, `#repository-paths` |
| `Link` / `page` / `per_page` pagination, total counts | `reshaped` | `#pagination` |
| GraphQL | `by-design-absent` | `#coming-from-github`. Decompose and count the fan-out. |
| Commit statuses (`statuses` permission, `POST /statuses/{sha}`) | `reshaped` | `#coming-from-github`, `#check-runs` |
| Issues (`issues` permission, `issues.*` events, `/issues/{n}` not on a pull request) | `by-design-absent` | `#coming-from-github`. Ask what the pull-request-scoped behavior should be. |
| `/issues/{n}/comments`, `/issues/{n}/labels` used on a pull request | `reshaped` | Pull requests endpoint reference; same calls under `/pulls/{n}/…` |
| Repository webhook CRUD (`/repos/…/hooks`) | `by-design-absent` | `#coming-from-github`, `#events` |
| App-manifest conversion, OAuth-app token mints | `by-design-absent` | `#installation`, Create App in the endpoint reference |
| Git Data API tree/blob writes | `by-design-absent` | `#git-https-authentication`; Git data endpoint reference |
| Standalone review-thread objects | `reshaped` | `#current-limitations`; Pull requests endpoint reference |
| User, email, team, and member lookups | `by-design-absent` | `#coming-from-github`, `#resource-references` |
| Single `pull_request` event with an `action` field, `previous_attributes` | `reshaped` | `#events`, `#event-payloads` |
| `x-github-*` headers, HMAC `x-hub-signature-256` | `reshaped` | `#headers`, `#signature-verification` |
| Payload inlines (changed files on push, before-SHA, `html_url`, `sender` profile) | `reshaped` | `#current-limitations`, `#resource-references`. Name the follow-up call per field and count the fan-out. |
| All events delivered after app creation | `reshaped` | `#events` |
| Reviews keyed by `commit_id` | `reshaped` | `#coming-from-github` |
| Finding own check runs or comments by actor | `reshaped` | `#check-runs` (`key`); comments and reviews by a marker the app controls |
| Requested-reviewer team pages, `created_via` | `by-design-absent` | Pull requests endpoint reference (reviewers by identifier) |

A feature that is not on this list and that the Origin docs never mention
(Marketplace billing, merge queues, Actions, Pages, Projects) is `unknown`
with a question, never `by-design-absent`.
