# Contributing to BridgetOS Open Source

## Filing an issue

Open issues on the upstream repository: https://github.com/theloopislooping/bridgetos-oss/issues

- **Bug report**: include the package name, Python version, minimal reproduction, and the full error output.
- **Feature request**: describe the use case, not just the solution. Mention which package is affected.
- Check existing issues before opening a new one.

## Opening a pull request

1. Fork the upstream repository and clone your fork.
2. Create a branch from `main`: `git checkout -b feat/my-change` or `fix/short-description`.
3. Make your change. Each package under `packages/` is independent — work inside its directory.
4. Ensure CI passes locally before pushing (see each package's `CONTRIBUTING.md` for commands).
5. Open a PR against `main` on the upstream repository with a clear description of what changed and why.

CI must be green before a PR is reviewed. One approving review is required to merge. PRs are merged via squash merge.

## Commit message convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/).

```
feat: add CrewAI adapter
fix: handle 429 rate-limit response in Client.observe
docs: clarify schema versioning rules
chore: bump ruff to 0.4.0
test: add prompt injection scenario assertions
```

The type prefix determines the changelog entry. Use `feat` for new behavior, `fix` for bug fixes, `docs` for documentation only, `chore` for tooling/deps, `test` for test-only changes.

Scope is optional but encouraged for monorepo clarity: `feat(langchain): ...`, `fix(sdk): ...`.

## Development setup

Each package is independently installable. See the package-specific `CONTRIBUTING.md` for setup commands, test instructions, and what counts as a breaking change.

| Package | CONTRIBUTING |
|---------|-------------|
| `bridgetos-schema` | [packages/bridgetos-schema/CONTRIBUTING.md](packages/bridgetos-schema/CONTRIBUTING.md) |
| `bridgetos-sdk-python` | [packages/bridgetos-sdk-python/CONTRIBUTING.md](packages/bridgetos-sdk-python/CONTRIBUTING.md) |
| `bridgetos-langchain` | [packages/bridgetos-langchain/CONTRIBUTING.md](packages/bridgetos-langchain/CONTRIBUTING.md) |
| `bridgetos-test-harness` | [packages/bridgetos-test-harness/CONTRIBUTING.md](packages/bridgetos-test-harness/CONTRIBUTING.md) |
