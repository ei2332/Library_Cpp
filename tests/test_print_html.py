"""Regression tests for the HTML mode and existing libparser CLI."""
import re
import subprocess
import sys
import unittest
from pathlib import Path

PARSER = Path(__file__).resolve().parents[1] / "scripts" / "libparser.py"

SOURCE = """//// @url https://example.org/lib
//// @name Example
//// @expl 説明です
//// @shade lazy
//// @check https://example.org/check include check
//// ! include
#include <x>
//// end
int a = 1;


//// expl 説明文
//// comp O(log n)
int b = 2;

int c = 3;
//// !! lazy
int lazy1 = 4;
//// ! lazy
//// text 補足
int lazy2 = 5;
//// end
//// ! check
int forbidden = 10;
//// end


"""


def cli(src, *options):
    return subprocess.run(
        [sys.executable, str(PARSER), *options], input=src,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8"
    )


class HtmlTests(unittest.TestCase):
    def test_cli_html_and_scope(self):
        h = cli(SOURCE, "--html")
        self.assertEqual(h.returncode, 0, h.stderr)
        self.assertIn("<h1>Example</h1>", h.stdout)
        self.assertNotIn("#include", h.stdout)
        self.assertNotIn("forbidden", h.stdout)
        self.assertIn("lazy1", h.stdout)
        self.assertIn("lazy2", h.stdout)
        self.assertEqual(h.stdout.count("code-row shaded"), 2)
        self.assertNotIn("example.org", h.stdout)

    def test_line_numbers_and_blank_trimming(self):
        h = cli(SOURCE, "--html")
        nums = [int(s) for s in re.findall(r'<span class="num">(\d+)</span>', h.stdout)]
        self.assertEqual(nums, [1, 2, 3, 4, 5, 6])
        self.assertIn("説明文", h.stdout)
        self.assertIn("計算量 O(log n)", h.stdout)
        self.assertNotIn(">comp ", h.stdout)

    def test_screen_two_columns_and_print_three_columns(self):
        h = cli(SOURCE, "--html")
        self.assertEqual(h.returncode, 0, h.stderr)
        self.assertIn('class="screen-layout"', h.stdout)
        self.assertIn('class="screen-code"', h.stdout)
        self.assertIn('class="screen-notes"', h.stdout)
        self.assertIn('grid-template-columns:minmax(0,65fr) minmax(310px,35fr)', h.stdout)
        self.assertIn('grid-template-columns:repeat(3,minmax(0,1fr))', h.stdout)
        self.assertIn('@page{size:A4 landscape;margin:0}', h.stdout)
        self.assertIn('id="print-pages"', h.stdout)
        self.assertIn('class="note-start"', h.stdout)
        self.assertIn('href="#line-2"', h.stdout)
        self.assertLess(h.stdout.index('data-no="6"'), h.stdout.index('class="note-start"'))
        self.assertIn('padding-left:2ch;text-indent:-2ch', h.stdout)

    def test_notes_are_attached_to_next_code_line(self):
        h = cli(SOURCE, "--html")
        self.assertEqual(h.returncode, 0, h.stderr)
        self.assertIn('href="#line-2"', h.stdout)
        self.assertIn('説明文', h.stdout)
        self.assertIn('計算量 O(log n)', h.stdout)
        self.assertIn('補足', h.stdout)
        self.assertNotIn('#include', h.stdout)

    def test_cpp_legacy_outputs(self):
        r = cli(SOURCE, "-s", "include")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("#include <x>", r.stdout)
        self.assertNotIn("int lazy1", r.stdout)
        self.assertEqual(cli(SOURCE, "-c").stdout.strip(), "1")
        self.assertEqual(cli(SOURCE, "-u").stdout.strip(), "https://example.org/lib")
        c = cli(SOURCE, "-c1")
        self.assertEqual(c.returncode, 0, c.stderr)
        self.assertIn("int forbidden", c.stdout)
        self.assertIn("https://example.org/check", c.stderr)

    def test_metadata_for_site_index(self):
        result = cli(SOURCE, "--metadata")
        self.assertEqual(result.returncode, 0, result.stderr)
        import json
        self.assertEqual(json.loads(result.stdout), {
            "name": "Example", "description": "説明です"
        })

    def test_html_escape_and_lexical_highlight(self):
        source = """//// @name X
bool a = (x < 5 && y > 0); // a&b
"""
        s = cli(source, "--html")
        self.assertEqual(s.returncode, 0, s.stderr)
        self.assertIn("&lt;", s.stdout)
        self.assertIn("&gt;", s.stdout)
        self.assertIn("&amp;&amp;", s.stdout)
        self.assertIn("a&amp;b", s.stdout)

    def test_unknown_shade_rejected(self):
        s = cli("//// @name X\n//// @shade lazy\nint a;\n", "--html")
        self.assertNotEqual(s.returncode, 0)
        self.assertIn("undefined scope", s.stderr)

    def test_included_scope_never_printed(self):
        s = cli("//// @name X\n//// @shade include\n//// ! include\nint a;\n//// end\n", "--html")
        self.assertNotEqual(s.returncode, 0)
        self.assertIn("not printable", s.stderr)

    def test_shade_works_even_before_declaration(self):
        s = cli("//// @shade extra\n//// @name X\n//// !! extra\nint x;\n", "--html")
        self.assertEqual(s.returncode, 0, s.stderr)
        self.assertIn("code-row shaded", s.stdout)

    def test_syntax_error_not_swallowed(self):
        s = cli("//// @expl Pollard's Rho\n//// @name X\n", "--html")
        self.assertNotEqual(s.returncode, 0)
        self.assertIn("No closing quotation", s.stderr)


if __name__ == "__main__":
    unittest.main()
