# Changelog

All notable changes to this plugin will be documented here.

## 0.1.0 — initial release

- Added the `origin-api` skill: fetch the live Origin docs and OpenAPI spec
  first, then apply the practices that hold across spec versions (credentials
  and token minting, minimal scopes, webhook verification and idempotency,
  opaque page tokens, TypeIDs, the error envelope, rate limits, and the
  deliberate differences from GitHub).
- Added the `port-github-app-to-origin` skill, built on `origin-api`: discover
  a GitHub App's surface from its codebase, map it onto the live Origin API
  spec, and write a porting brief with a capability table, webhook field map,
  hello-world path, gap cards, and up-front questions.
