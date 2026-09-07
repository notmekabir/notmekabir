# Final Dynamic GitHub Profile

Upload the **entire contents** of this package into:

`notmekabir/notmekabir`

on the `main` branch.

## Included

```text
README.md
MYreadme.md
SETUP.md
update_profile.py
requirements.txt

assets/
├── dark_mode.svg
├── light_mode.svg
├── matrix-portrait.png
├── circuit-divider.svg
└── contribution-activity.svg

.github/
└── workflows/
    └── update-profile.yml
```

The first workflow run also generates:

```text
assets/github-snake.svg
assets/github-snake-dark.svg
```

## Dynamic pieces

The main Matrix SVG is regenerated with live GitHub telemetry:

- total repositories
- stars
- followers
- following
- contributions over the last 365 days
- last sync time

The contribution activity heatmap is generated locally from GitHub's contribution calendar.

The snake is generated automatically by the GitHub Action and tracks the contribution calendar.

## First run

After uploading all files:

**GitHub → Actions → Update dynamic profile → Run workflow**

Wait for completion, then refresh your profile with:

`Ctrl + F5`

## Why the contribution graph is local

The previous third-party activity graph endpoint has experienced deployment/billing outages. This version generates the graph inside your own repository with the GitHub API, so your README is not dependent on that external deployment.

## Snake

The snake generation uses the `Platane/snk` GitHub Action. It generates light and dark SVG files and commits them into your repository. The README references those local files.

## Important

Do not delete the `.github/workflows/update-profile.yml` file. It is what keeps the profile assets dynamic.
