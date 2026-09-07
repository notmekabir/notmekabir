# Cyberpunk GitHub Profile Setup

## 1. Repository

Create/use the special GitHub profile repository:

`https://github.com/notmekabir/notmekabir`

The repository must be public.

## 2. Copy these files

- `README.md`
- `update_profile.py`
- `requirements.txt`
- `assets/dark_mode.svg`
- `assets/light_mode.svg`
- `.github/workflows/update-profile.yml`

## 3. Run the workflow

Open **Actions → Update profile SVG → Run workflow**.

The workflow also runs automatically every day.

## 4. Token

No personal access token is required. The workflow uses GitHub's built-in `GITHUB_TOKEN`.

## 5. Theme behavior

GitHub uses the `<picture>` element to select the dark or light SVG based on the viewer's color-scheme preference.

## 6. If the SVG does not animate

GitHub and browser rendering can differ for animated SVGs. The profile still has a static fallback appearance, and the dynamic telemetry is updated by the workflow.
