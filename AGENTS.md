# GitHub profile maintenance

Read [the maintenance guide](docs/profile-maintenance.md) before editing. The root
`README.md` is Eitan's public GitHub profile; keep maintenance material out of it.

## Profile rules

- Use only GitHub-flavored Markdown and supported HTML. Do not add a custom
  site, scripts, styles, iframes, external image services, or language and theme
  controls. Important content and the terminal joke must be visible without clicks.
- Keep the copy concise, natural, and in English. Introduce Eitan as an
  AI-native developer and vibe coder. Use lowercase `vibe coder` in sentences.
  Keep the humor dry and technical; do not invent credentials or add a project
  list, Unity/audio content, or extra links without an explicit request.
- Preserve the restrained silver, black, and ice-blue treatment. Keep typography
  legible at phone widths. Use a single glass-style focal graphic and a small
  set of badges; avoid animation, visual clutter, and unnecessary decoration.
- Store covers in `assets/banners/` and badges/contact icons in `assets/badges/`.
  Use local WebP pairs with matching dimensions and descriptive alt text. Use
  GitHub-supported `<picture>` markup to follow light/dark appearance automatically;
  the ordinary `<img>` must be the light fallback.

## Before publishing

1. Run `python3 scripts/validate_profile.py` and `git diff --check`.
2. For a README or image change, preview the rendered profile in light and dark
   mode at desktop and narrow mobile widths. Check links, readability, and that
   both variants load. Record observed results, not assumptions.
3. Keep changes scoped. Do not commit previews, raw exports, generated bundles,
   caches, or private material. Preserve icon license notices.
4. Use a branch and pull request unless the owner explicitly authorizes
   direct publication. Never force-push. CI checks changes but does not edit
   the profile, commit, or publish on behalf of the owner.
