# Origin-isms: GitHub surfaces Origin departs from on purpose

Check here before labeling anything `gap`. A row below is `by-design-absent`
or `reshaped`; the brief points at the idiom and never files a card. The
reasoning behind each lives in the `origin-api` skill; this table carries only
what the classifier needs. Confirm current wording in `llms-full.txt`.

| GitHub surface the app uses | Label | Origin idiom |
| --- | --- | --- |
| Acting on a repository mirrored *from* GitHub (writes, `push` events) | `by-design-absent` | Install on Origin-native repositories or stable outbound mirrors. Mirrors are read-only to apps and deliver no `repository.pushed`. First question of every brief. |
| Install callback with `installation_id` + `setup_action` query params | `reshaped` | Signed installation receipt JWT; `sub` is the installation ID. Not a Bearer. |
| RS256 app JWT | `reshaped` | EdDSA over Ed25519; register the public key. |
| `ghs_` installation tokens, long cache | `reshaped` | `oit_…`, short-lived, minted just in time, attenuable to scopes and `repositoryIds`. |
| User OAuth: `/user`, `/user/installations`, `/user/repos`, install-by-user picker | `by-design-absent` | Repository discovery is `/installation/repos`. App creation and installation-repository changes are admin actions with a user credential, not app calls. Ask what the flow should do. |
| Permissions `<noun>: read\|write` | `reshaped` | Scopes `repository:<noun>[:<sub>]:<read\|write>` taken from `x-origin-scopes` of the called operations. |
| Numeric IDs, `/repositories/{id}` | `reshaped` | TypeIDs; `/repos/_/{repoId}`. |
| `Link` / `page` / `per_page` pagination, total counts | `reshaped` | `pageSize` / `pageToken` / `nextPageToken`; opaque; no total. |
| GraphQL | `by-design-absent` | REST; decompose and count the fan-out. |
| Commit statuses (`statuses` permission, `POST /statuses/{sha}`) | `reshaped` | Check runs upserting on a caller-stable `key`; rulesets bind on the key. |
| Issues (`issues` permission, `issues.*` events, `/issues/{n}` not on a PR) | `by-design-absent` | PR comments, threads, reviews, labels on pull requests. Ask what the PR-scoped behavior should be. |
| `/issues/{n}/comments`, `/issues/{n}/labels` used on a pull request | `reshaped` | Same calls under `/pulls/{n}/…`. |
| Repository webhook CRUD (`/repos/…/hooks`) | `by-design-absent` | Subscriptions are app settings. |
| App-manifest conversion, OAuth-app token mints | `by-design-absent` | App creation form (accepts prefill params) or user-credential `CreateApp`. |
| Git Data API tree/blob writes | `by-design-absent` | Push over Git HTTPS with an installation token, or the documented commit-from-files and ref operations. |
| Standalone review-thread objects | `reshaped` | A thread materializes from its first diff-anchored comment and is addressable for resolve/reopen. |
| User, email, team, and member lookups | `by-design-absent` | Actors are TypeIDs (plus a handle where exposed). No directory. |
| Single `pull_request` event with `action` field, `previous_attributes` | `reshaped` | One slug per action (`pull_request.head_ref.pushed`); no `action` field, no delta. Confirm each slug in `x-origin-webhook-events`. |
| `x-github-*` headers, HMAC `x-hub-signature-256` | `reshaped` | `webhook-*` headers; `v1ed` Ed25519 over a SHA-256 digest, JWKS keys. |
| Payload inlines: changed files on push, before-SHA, `html_url`, `sender` profile | `reshaped` | Follow-up `Get…` / `CompareCommits` / `ListComparisonFiles` with identifiers the payload carries. Name the call per field; count the fan-out. |
| Default delivery of all events after app creation | `reshaped` | Only installation lifecycle is default; select the rest. |
| Reviews keyed by `commit_id` | `reshaped` | Reviews anchor to a pull request version. |
| Finding own check runs / comments by actor | `reshaped` | Check runs by `key`; comments and reviews by a marker the app controls. |
| Requested-reviewer team pages, `created_via` | `by-design-absent` | Reviewers addressed by identifier only. |

Not on this list, and not mentioned anywhere in the Origin docs (Marketplace
billing, merge queues, Actions, Pages, Projects): `unknown` with a question,
never `by-design-absent`.
