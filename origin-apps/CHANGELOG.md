# Changelog

All notable changes to this plugin will be documented here.

## 0.1.0, initial release

- Added the `origin-api` skill. It lists the live Origin docs and OpenAPI spec
  to fetch first, then the Origin rules that GitHub habits get wrong:
  credentials and token minting, minimal scopes, webhook verification and
  idempotency, opaque page tokens, TypeIDs, the error envelope, rate limits,
  and the differences from GitHub that are decisions rather than gaps.
- Added the `port-github-app-to-origin` skill, built on `origin-api`. It reads
  what a GitHub App uses from GitHub out of its codebase, maps that onto the
  live Origin spec, and writes a porting brief with a capability table, a
  webhook field map, a hello-world path, gap cards, and up-front questions.
