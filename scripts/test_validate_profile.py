import re
import shutil
import tempfile
import unittest
from pathlib import Path

from validate_profile import ROOT, validate


class ProfileValidationTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.readme = self.root / "README.md"
        shutil.copyfile(ROOT / self.readme.name, self.readme)
        shutil.copytree(ROOT / "assets", self.root / "assets")

    def edit_readme(self, pattern, replacement):
        text = self.readme.read_text(encoding="utf-8")
        changed, count = re.subn(pattern, replacement, text, count=1)
        self.assertEqual(count, 1)
        self.readme.write_text(changed, encoding="utf-8")

    def test_current_profile(self):
        pictures, totals = validate(self.root)
        self.assertGreaterEqual(pictures, 1)
        self.assertTrue(all(totals.values()))

    def test_missing_dark_source(self):
        self.edit_readme(r'<source\s+media="\(prefers-color-scheme: dark\)"[^>]*>', "")
        with self.assertRaisesRegex(ValueError, "needs light, dark and fallback"):
            validate(self.root)

    def test_missing_asset(self):
        missing = next((self.root / "assets" / "banners").glob("*-dark.webp"))
        missing.unlink()
        with self.assertRaisesRegex(ValueError, "Asset missing"):
            validate(self.root)

    def test_wrong_fallback_path(self):
        self.edit_readme(r'(<img\s+src=")[^"]+', r'\g<1>./bad-path.webp')
        with self.assertRaisesRegex(ValueError, "fall back to its light source"):
            validate(self.root)

    def test_over_budget_asset(self):
        banner = next((self.root / "assets" / "banners").glob("*-dark.webp"))
        with banner.open("ab") as output:
            output.write(b"\0" * 20_001)
        with self.assertRaisesRegex(ValueError, r"bytes \(limit 20,000\)"):
            validate(self.root)

    def test_javascript_is_not_profile_markup(self):
        with self.readme.open("a", encoding="utf-8") as output:
            output.write("\n<script></script>\n")
        with self.assertRaisesRegex(ValueError, "<script> is not allowed"):
            validate(self.root)


if __name__ == "__main__":
    unittest.main()
