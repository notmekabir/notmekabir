# Fully fixed GitHub profile package

## Upload everything at once

This package is designed for your special profile repository:

`notmekabir/notmekabir`

Upload **everything inside this folder** to the repository root and commit it to `main`.

The README uses only repository-local PNG files:

```text
assets/profile-dark.png
assets/profile-light.png
```

This deliberately avoids the SVG rendering problem you were seeing.

The supplied Matrix portrait is stored at:

```text
assets/matrix-portrait.png
```

and is built into the profile card image by `generate_profile.py`.

## Required repository structure

```text
notmekabir/
├── README.md
├── MYreadme.md
├── generate_profile.py
├── requirements.txt
├── SETUP.md
├── assets/
│   ├── matrix-portrait.png
│   ├── profile-dark.png
│   └── profile-light.png
└── .github/
    └── workflows/
        └── update-profile.yml
```

## After upload

1. Open **Actions**.
2. Select **Update profile card**.
3. Click **Run workflow**.
4. Wait for it to finish.
5. Open your profile and press `Ctrl + F5`.

The first upload already contains working PNG cards with placeholder telemetry. The Action replaces the placeholder numbers with live GitHub data.

## No personal access token

The workflow uses GitHub's built-in:

```text
GITHUB_TOKEN
```

No PAT is required.

## Important

Do not delete `profile-dark.png` or `profile-light.png` after the first upload. They are the files the README actually displays.

The old `dark_mode.svg` and `light_mode.svg` are intentionally not used anymore.
