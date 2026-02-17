# THIRD-PARTY NOTICES

This file summarizes third-party rights and attribution scope for this repository.

## 1. Repository License

- This repository's original code/docs are licensed under MIT.
- See `LICENSE`.

## 2. Runtime Dependency (Distributed by install, not vendored)

### `mcp` (version pinned in this project: `1.26.0`)

- License: MIT
- Upstream: <https://github.com/modelcontextprotocol/python-sdk>
- Note: this repository does not vendor `mcp` source code; it is installed as a dependency.

## 3. Build-Time Tooling (Not shipped as repository content)

### `setuptools` / `wheel`

- License expression (PyPI metadata): MIT
- Upstream:
  - <https://github.com/pypa/setuptools>
  - <https://github.com/pypa/wheel>
- Note: these are packaging/build tools and are not redistributed as part of this repository content.

## 4. Data Source Terms (Legal Content from e-Gov)

- e-Gov terms: <https://laws.e-gov.go.jp/terms/>
- This repository documents attribution/editing requirements in `NOTICE.md`.
- When redistributing outputs containing e-Gov-derived legal content, follow `NOTICE.md`.

## 5. Development-Only Tools

Tools used during development (for example `git`, `gh`, `uv`, local Python runtime, editors, CI runners) are not redistributed as part of this repository artifacts, so no additional in-repo attribution is required solely for using those tools.

## 6. Generated Output Responsibility

Even when drafts are generated with automation/LLMs, distributors remain responsible for:

1. respecting upstream terms for included source content,
2. avoiding third-party rights infringement in redistributed materials, and
3. adding required attribution/edit notices when applicable.
