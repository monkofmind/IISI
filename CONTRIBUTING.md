# Contributing to IISI

Thank you for your interest. IISI is proprietary software.

## What we welcome

- Bug reports via GitHub Issues
- Policy pack contributions (domain-specific YAML)
- Connector implementations (LLM providers, enterprise systems)
- Documentation improvements
- Test coverage expansions

## What requires a signed agreement

- Core architecture modifications
- Stabilization mechanism changes
- New distortion classes
- Changes to the Stability Index formula

Contact founder@mindtechos.com before submitting PRs in these areas.

## Code standards

- Python 3.9+
- Zero external dependencies for `iisi/` core
- All new code must include tests
- Run `pytest tests/ -v` before submitting

## Semantic versioning

- `0.x.y` — pre-1.0, API may change
- `1.x.y` — stable API, breaking changes = major bump
