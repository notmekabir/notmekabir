# Dynamic SVG GitHub Profile

This is the SVG version you asked for.

## Upload everything

Upload the entire contents of this package into:

`notmekabir/notmekabir`

on the `main` branch.

### Repository structure

```text
notmekabir/
├── README.md
├── MYreadme.md
├── SETUP.md
├── requirements.txt
├── update_profile.py
├── assets/
│   ├── dark_mode.svg
│   ├── light_mode.svg
│   └── matrix-portrait.png
└── .github/
    └── workflows/
        └── update-profile.yml
```

## What is dynamic?

The SVG is regenerated from GitHub data. The workflow updates:

- repository count
- stars
- followers
- following
- contributions during the last 365 days
- last synchronization time

The workflow runs daily and can also be started manually.

The SVG animation is separate from the telemetry update: Matrix rain, scanlines, glow, and cursor effects are encoded in the SVG itself.

## Important change from the previous version

The README uses **relative repository paths**:

```html
<source media="(prefers-color-scheme: dark)" srcset="./assets/dark_mode.svg">
<img src="./assets/light_mode.svg">
```

The portrait is embedded directly into the SVG as base64 image data. Nothing inside the SVG needs to fetch the portrait from another server.

GitHub documents relative image paths in rendered README files as supported and resolves them against the current branch. 

## GitHub Actions permissions

The workflow declares:

```yaml
permissions:
  contents: write
```

This is required because the workflow updates the SVG files in the repository. GitHub documents that `GITHUB_TOKEN` permissions can be set with the workflow `permissions` key.

## After uploading

Go to:

**Actions → Update dynamic SVG profile → Run workflow**

Wait for the workflow to finish, then open:

`https://github.com/notmekabir`

and refresh with `Ctrl + F5`.

If GitHub shows an old image temporarily, wait a little for the cached image to refresh after the commit.
