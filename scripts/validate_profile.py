#!/usr/bin/env python3
"""Validate the public README and its local theme assets using the standard library."""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = re.compile(r"\./assets/(banners|badges)/[a-z0-9]+(?:-[a-z0-9]+)*\.webp")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
BUDGET = {"banners": 6_000, "badges": 1_500}
THEME_BUDGET = 13_000
MEDIA = {f"(prefers-color-scheme: {theme})": theme for theme in ("light", "dark")}


def require(condition, message):
    if not condition:
        raise ValueError(message)


class ProfileMarkup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.pictures = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        require(tag not in {"script", "style", "iframe", "link", "form", "button", "input",
                            "select", "details", "video", "audio", "object", "embed", "svg", "canvas"},
                f"<{tag}> is not allowed in the public profile")
        require(not any(name == "style" or name.startswith("on") for name in attrs),
                f"<{tag}> must not contain custom CSS or event handlers")
        if tag == "picture":
            require(self.current is None, "Nested <picture> is not supported")
            self.current = {}
        elif tag == "source":
            require(self.current is not None, "<source> must be in a <picture>")
            theme = MEDIA.get(attrs.get("media"))
            require(theme is not None, "Image sources must use light or dark prefers-color-scheme")
            require(theme not in self.current, f"Duplicate {theme} source in one <picture>")
            require("fallback" not in self.current, "Theme sources must precede the fallback <img>")
            self.current[theme] = attrs.get("srcset") or ""
        elif tag == "img":
            require(self.current is not None, "Profile images must use a theme-aware <picture>")
            require("fallback" not in self.current, "Only one fallback <img> per <picture>")
            require(bool((attrs.get("alt") or "").strip()), "Each fallback <img> needs descriptive alt text")
            self.current["fallback"] = attrs.get("src") or ""

    def handle_endtag(self, tag):
        if tag == "picture":
            require(self.current is not None, "Stray </picture>")
            self.pictures.append(self.current)
            self.current = None


def unfenced_lines(text):
    fence = None
    for line in text.splitlines():
        match = FENCE.match(line)
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
        elif match:
            fence = match[1]
        else:
            yield line
    require(fence is None, "Unclosed fenced code block")


def webp_dimensions(path):
    data = path.read_bytes()
    integer = lambda value: int.from_bytes(value, "little")
    require(len(data) >= 20 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
            and integer(data[4:8]) + 8 == len(data), f"Invalid WebP header: {path.name}")
    kind = data[12:16]
    size = integer(data[16:20])
    header = data[20:20 + size]
    require(len(header) == size, f"Truncated WebP chunk: {path.name}")
    if kind == b"VP8X" and len(header) == 10:
        return integer(header[4:7]) + 1, integer(header[7:10]) + 1
    if kind == b"VP8 " and len(header) >= 10 and header[3:6] == b"\x9d\x01\x2a":
        return integer(header[6:8]) & 0x3FFF, integer(header[8:10]) & 0x3FFF
    if kind == b"VP8L" and len(header) >= 5 and header[0] == 0x2F:
        bits = integer(header[1:5])
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    raise ValueError(f"Unsupported WebP header: {path.name}")


def validate(root):
    readme = root / "README.md"
    require(readme.stat().st_size <= 12_000, "README exceeds 12,000 bytes")
    markup = ProfileMarkup()
    text = "\n".join(unfenced_lines(readme.read_text(encoding="utf-8")))
    require("![" not in text, "Use a theme-aware <picture> instead of a Markdown image")
    markup.feed(text)
    markup.close()
    require(markup.current is None, "Unclosed <picture>")
    require(markup.pictures, "At least one theme-aware picture is required")

    used = {"light": {}, "dark": {}}
    banner_count = 0
    for i, pair in enumerate(markup.pictures, start=1):
        require(set(pair) == {"light", "dark", "fallback"}, f"Picture {i} needs light, dark and fallback images")
        light, dark = pair["light"], pair["dark"]
        require(light == pair["fallback"], f"Picture {i} must fall back to its light source")
        light_stem = light.removesuffix(".webp").removesuffix("-light")
        require(dark == light_stem + "-dark.webp",
                f"Picture {i} needs matching names with the -dark suffix")

        dimensions = []
        for theme, name in (("light", light), ("dark", dark)):
            match = IMAGE.fullmatch(name)
            require(match is not None, f"Picture {i} uses a nonlocal or invalid WebP path: {name!r}")
            directory = match[1]
            path = root / name[2:]
            require(path.is_file() and path.resolve().is_relative_to(root.resolve()),
                    f"Asset missing or outside repository: {name}")
            size = path.stat().st_size
            require(0 < size <= BUDGET[directory], f"{name}: {size:,} bytes (limit {BUDGET[directory]:,})")
            used[theme][name] = size
            dimensions.append(webp_dimensions(path))
        require(dimensions[0] == dimensions[1] and all(dimensions[0]),
                f"Picture {i} has mismatched or invalid light/dark dimensions")
        banner_count += light.startswith("./assets/banners/")

    require(banner_count == 1, "The README should show exactly one banner")
    totals = {theme: sum(assets.values()) for theme, assets in used.items()}
    for theme, total in totals.items():
        require(total <= THEME_BUDGET,
                f"{theme.title()} assets total {total:,} bytes (limit {THEME_BUDGET:,})")
    expected = set(used["light"]) | set(used["dark"])
    actual = {"./" + path.relative_to(root).as_posix()
              for path in (root / "assets").rglob("*.webp")}
    require(expected == actual, "Unreferenced WebP assets: " + ", ".join(sorted(actual - expected)))
    return len(markup.pictures), totals


if __name__ == "__main__":
    try:
        pictures, totals = validate(ROOT)
    except (OSError, ValueError) as error:
        sys.exit(f"Profile check failed: {error}")
    print(f"Profile check passed: {pictures} picture pairs; "
          f"light {totals['light']:,} bytes; dark {totals['dark']:,} bytes.")
