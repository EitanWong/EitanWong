# Profile maintenance

GitHub renders the root `README.md` directly on the account profile. Nothing is
built or hosted separately. See [AGENTS.md](../AGENTS.md) for repository-wide
instructions.

## Theme assets

Each banner, tool badge, and contact icon needs a matching light and dark WebP.
Use the same pixel dimensions for both variants to avoid layout shifts. Do not
rely on custom CSS, JavaScript, or background colors from GitHub to make text
inside an image legible.

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/banners/profile-dark.webp">
  <source media="(prefers-color-scheme: light)" srcset="./assets/banners/profile-light.webp">
  <img src="./assets/banners/profile-light.webp" alt="Eitan. AI-native developer and vibe coder." width="100%">
</picture>
```

Keep the current 1440 x 552 cover proportions unless intentionally redesigning
both themes. Render badges crisp at their displayed height (28 or 30 px today).
Give meaningful images descriptive alt text; an image that is the only content
of a link needs alt text that names the destination. Preview the actual GitHub
layout; not all standard HTML or browser features are available in a README.

## Compression budgets

| Asset | Limit |
| --- | ---: |
| One banner variant | 20,000 bytes |
| One badge or contact icon variant | 6,000 bytes |
| All unique images used by one theme | 50,000 bytes |
| Root README | 12,000 bytes |

Export only the final WebP versions. Use lossless compression for badges and
compare lossy cover exports at the displayed size before choosing one. A starting
point with Google's WebP tools:

```sh
cwebp -q 88 -m 6 -sharp_yuv -metadata none cover.png -o profile-light.webp
cwebp -lossless -z 9 -metadata none badge.png -o badge.webp
```

Keep the Lucide notice with the installed icons. Use relative, case-sensitive
paths and do not leave unreferenced WebP exports in the asset directories.

## Checks and rollout

Run `python3 scripts/validate_profile.py` (Python 3.9+, standard library only).
GitHub Actions runs the same check on pull requests and pushes to `main`.
It checks markup, paths, WebP headers, matching dimensions, and byte budgets;
it does not judge visual design or test external contact destinations.
When changing the validator, also run `python3 -B -m unittest discover -s scripts -v`.

Before publishing a content change, view the rendered README in both themes at
desktop and mobile widths. Check the headline, alt text, contact links, and
terminal block. Keep the commit scoped to the relevant README and assets. To
roll back a published change, revert its commit rather than rewriting history.

References: [GitHub's picture support](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#the-picture-element),
[Apple Materials](https://developer.apple.com/design/human-interface-guidelines/materials),
and [Apple Dark Mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode).
