# Contributing

## Branch & PR workflow

**Never push directly to `main`.** All changes must go through a pull request.

1. Create a branch off `main`:
   ```bash
   git checkout main && git pull
   git checkout -b <type>/<short-description>
   # e.g. feat/circle-notifications, fix/end-date-bug, chore/update-deps
   ```

2. Make your changes and commit with a descriptive message.

3. Push your branch and open a PR against `main`:
   ```bash
   git push -u origin <branch-name>
   gh pr create
   ```

4. Merging to `main` triggers the deploy workflow automatically.

## Branch naming

| Prefix | Use for |
|--------|---------|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `chore/` | Deps, config, tooling |
| `ci/` | CI/CD changes |
| `docs/` | Documentation only |

## Commit style

Keep messages short and imperative:
```
feat: add payout scheduling endpoint
fix: correct end date for bi-weekly frequency
chore: bump python-dateutil to 2.9.0
```
