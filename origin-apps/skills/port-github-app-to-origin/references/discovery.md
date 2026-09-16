# Discovering the GitHub App's shape from the codebase

Everything the brief needs about the existing app is in the repository. Search
for it; do not ask for it. Record a file and line for every fact so the team
can check your reading, and record every place you looked that turned up
nothing so they can point you at the right place if you missed it.

Work through the seven facets below. The searches are starting points across
the common ecosystems (Node Octokit and Probot, Go `go-github`, Python
`PyGithub`/`ghapi`/`githubkit`, Java `hub4j`, Ruby `octokit.rb`, .NET
`Octokit.net`, raw HTTP in any language); extend them when the code uses
something else. Note the language and libraries you observe as a fact in the
inventory — they inform sizes in the brief and nothing else.

## 1. Declared permissions and events

The app's manifest or registration snapshot, if it is checked in.

- Files: `app.yml`, `app.yaml`, `.github/app.yml`, `github-app-manifest.json`,
  `manifest.json`, `app-manifest.*`, Terraform or Pulumi resources for the
  app, and infrastructure-as-code that seeds a GitHub App.
- Keys: `default_permissions`, `default_events`, `hook_attributes`,
  `redirect_url`, `callback_urls`, `setup_url`, `public`,
  `request_oauth_on_install`, `setup_on_update`.
- Probot: `app.yml` at the repo root carries `default_events` and
  `default_permissions`.

When there is no manifest, derive the effective permissions from the calls in
facet 4 and say the manifest was absent. The union of what the code calls is
what the port needs anyway.

## 2. Webhook events handled

- Probot / `@octokit/webhooks`: `app.on("<event>.<action>", …)`,
  `app.on([...])`, `webhooks.on(`, `webhooks.onAny(`, `EmitterWebhookEvent`.
- Hand-rolled receivers: a `switch` or dispatch on the `x-github-event` header
  (any casing), on `payload.action`, or on a combined `"<event>.<action>"`
  string; Go `github.WebHookType(r)` / `github.ParseWebHook`; Python
  `request.headers["X-GitHub-Event"]`.
- Framework routes registered for webhook paths: `/webhook`, `/webhooks`,
  `/github/webhooks`, `/api/github/events`, `createNodeMiddleware`,
  `createProbot`, smee/ngrok tunnel config in development scripts.

For each handled event record the GitHub event, the action(s) handled, the
handler location, and — from facet 3 — which payload fields it reads.

## 3. Payload fields read

Inside each handler from facet 2, list every property path dereferenced from
the payload object: `payload.pull_request.head.sha`, `payload.repository.name`,
`payload.installation.id`, `payload.sender.login`, `payload.commits[].added`,
`payload.check_suite.pull_requests`, `payload.before`, `payload.after`, and so
on. Typed languages make this easy (struct fields accessed); in dynamic
languages grep the handler body and any helper it passes the payload to.
Include fields used only for logging or metrics — those are the ones teams
forget until the port breaks a dashboard.

## 4. REST and GraphQL calls

- Octokit REST: `octokit.rest.<namespace>.<method>(`, `octokit.<namespace>.<method>(`,
  `octokit.request("<METHOD> /…")`, `octokit.paginate(`, `octokit.graphql(`,
  `@octokit/graphql`, `.graphql(`.
- Other SDKs: Go `client.PullRequests.`, `client.Checks.`, `client.Repositories.`,
  `client.Issues.`, `client.Apps.`; Python `repo.get_pull(`, `gh.rest.`,
  `githubkit`; Java `GHRepository`, `GHPullRequest`; Ruby `client.pull_request(`.
- Raw HTTP: `api.github.com`, `/repos/`, `Accept: application/vnd.github`,
  `X-GitHub-Api-Version`, `uploads.github.com`, `raw.githubusercontent.com`.
- GraphQL documents: `.graphql` / `.gql` files, template strings starting with
  `query` or `mutation`, generated client code.

Record each distinct call family once (method + path, or SDK method), with
the parameters and filters the code passes (state, base, head, per_page,
sort, since, check_name, app_id, filter…), the response fields it reads, and
whether it is called in a loop or per webhook (this decides the fan-out
tradeoff on the brief row). Note pagination style in use (`Link` header,
`page`/`per_page`, `octokit.paginate`, GraphQL cursors) — it always changes.

## 5. Authentication and token minting

- App identity: `GITHUB_APP_ID`, `APP_ID`, `GITHUB_PRIVATE_KEY`, `PRIVATE_KEY`,
  `.pem` files, `createAppAuth`, `@octokit/auth-app`, `ghinstallation`
  (Go), `jwt.encode(... "RS256")`, `App.get_installation(`.
- Installation tokens: `/app/installations/{id}/access_tokens`,
  `installationId`, `installation_id`, `app.auth(`, `getInstallationOctokit(`,
  `ghs_` prefixes in tests or fixtures, token caches keyed by installation.
- User OAuth: `/login/oauth/authorize`, `/login/oauth/access_token`,
  `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `@octokit/auth-oauth-*`,
  `/user`, `/user/installations`, `/user/repos`, "setup URL" handlers reading
  `installation_id` and `setup_action` from the callback query string.
- Git over HTTPS as the app: `x-access-token:` in clone URLs, credential
  helpers, `GIT_ASKPASS`.

Record the flows present: app JWT algorithm, how the installation is
identified after install (callback query, webhook, or DB), token lifetime
handling, whether user OAuth exists and what it is used for (identity,
repo discovery, acting on behalf of a user), and whether the app pushes or
clones git.

## 6. Webhook receiver and verification

- Signature: `x-hub-signature-256`, `x-hub-signature`, `verify(`,
  `verifyAndReceive(`, `WEBHOOK_SECRET`, HMAC-SHA256 helpers,
  `github.ValidatePayload`.
- Delivery handling: use of `x-github-delivery` for idempotency, queueing
  before or after responding, retry handling, redelivery tooling against
  `/app/hook/deliveries`.
- Transport: the public URL and how it is configured (manifest
  `hook_attributes.url`, env var, tunnel in dev).

Record the verification scheme, whether the raw body is available at
verification time (frameworks that parse JSON first cannot verify), and how
deliveries are deduplicated, if at all.

## 7. Calls the framework makes on the app's behalf

Some of the app's GitHub surface is not in its own source: it is what the
framework or a helper library does for it, and the port has to do it too.
When the code uses one of these, list the calls the dependency makes as rows
in their own right, marked "from `<dependency>` (documented behavior)" so the
team knows they were inferred, not read. `node_modules` is usually not
checked in, so read the dependency's README or its source on its own
repository, not the app.

- **Probot**: the built-in receiver (`POST /`, `@octokit/webhooks` HMAC
  verification, `x-github-event` routing), per-installation token minting
  and caching, `context.repo()` / `context.issue()` helpers,
  `context.isBot` (`payload.sender.type`). Common companions:
  `probot-config` (reads `.github/<file>.yml`, falling back to the owner's
  `.github` repository), `probot-scheduler` (lists installations and their
  repositories with the app credential, then emits `schedule.repository` on
  an interval), `probot-metadata` (stores state in issue bodies).
- **Octokit `App` / `@octokit/app`**: `app.webhooks.verifyAndReceive`,
  `app.eachInstallation` / `app.eachRepository` (installation + repository
  listing), automatic installation-token minting behind
  `app.getInstallationOctokit`.
- **Go `ghinstallation`, Python `githubkit`/`gidgethub`, Ruby `octokit`
  app auth**: JWT minting and installation-token exchange.
- **Frameworks' webhook middleware** in any language: which header names
  they read and whether they verify against the raw body.

## When something is missing

Say so in the inventory: "no manifest found (searched: …)", "no signature
verification found in the receiver at …", "GraphQL client present but no
query documents found". Each missing item becomes either a row with an
`unknown` label or an up-front question in the brief. Do not fill gaps with
assumptions about what an app of this kind usually does.
