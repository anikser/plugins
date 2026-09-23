# Discovering the GitHub App's shape from the codebase

Everything the brief needs about the app is in the repository. Search; do not
ask. Record `file:line` for every fact and list every place you looked that
turned up nothing. Note the language and libraries as an observation; they
inform sizes and nothing else.

Seven facets. For each, what to record:

1. **Declared permissions and events.** The manifest or registration snapshot
   if checked in (`app.yml`, manifest JSON, IaC that seeds the app; Probot
   keeps `default_events` / `default_permissions` in `app.yml`). If absent,
   say so and derive permissions from facet 4; the union of what the code
   calls is what the port needs anyway.
2. **Webhook events handled.** Each GitHub event and action pair the code
   dispatches on (`app.on("pull_request.opened")`, a switch on
   `x-github-event` + `payload.action`, SDK parsers), with the handler
   location.
3. **Payload fields read.** Every property path dereferenced from the payload
   inside each handler and the helpers it passes the payload to. Include
   fields used only for logging or metrics; those break dashboards after the
   port.
4. **REST and GraphQL calls.** Each distinct call family once (method + path
   or SDK method) with the parameters and filters passed, the response fields
   read, whether it runs per webhook or in a loop (decides the fan-out
   tradeoff), and the pagination style in use (it always changes). GraphQL
   documents count as calls; they are decomposed during mapping.
5. **Authentication and token minting.** App JWT algorithm; how the
   installation is identified after install (callback query, webhook, DB);
   token lifetime handling; whether user OAuth exists and for what (identity,
   repository discovery, acting for a user); whether the app clones or pushes
   git as itself.
6. **Webhook receiver and verification.** Signature scheme; whether the raw
   body is available at verification time (frameworks that parse JSON first
   cannot verify); how deliveries are deduplicated, if at all; where the
   public URL is configured.
7. **Calls the framework makes on the app's behalf.** Not in the app's
   source, but the port has to do them. List them as rows marked "from
   `<dependency>` (documented behavior)" and read the dependency's docs or
   source, not the app. Common cases:
   - **Probot**: built-in receiver and HMAC verification, per-installation
     token minting and caching, `context.repo()` / `context.issue()`,
     `context.isBot`; companions `probot-config` (reads `.github/<file>.yml`,
     falling back to the owner's `.github` repository), `probot-scheduler`
     (lists installations and repositories with the app credential, emits
     `schedule.repository`), `probot-metadata` (state in issue bodies).
   - **Octokit `App`**: `webhooks.verifyAndReceive`, `eachInstallation` /
     `eachRepository`, automatic token minting behind
     `getInstallationOctokit`.
   - **`ghinstallation`, `githubkit`, `gidgethub`, `octokit.rb` app auth**:
     JWT minting and installation-token exchange.

When something is missing, say so in the inventory ("no manifest found
(searched: …)", "no signature verification found in the receiver at …").
Each missing item becomes an `unknown` row or an up-front question. Do not
fill gaps with what an app of this kind usually does.
