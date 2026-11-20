#!/usr/bin/env python3
"""Build the print HTML pages and library index using libparser.py."""

import argparse
from html import escape
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "src"
PARSER = ROOT / "scripts" / "libparser.py"
EXTENSIONS = {".cpp", ".hpp", ".h", ".cc", ".cxx"}


def parse(source: bytes, option: str) -> str:
    result = subprocess.run(
        [sys.executable, str(PARSER), option],
        input=source, capture_output=True, check=False, timeout=60,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout.decode("utf-8")


def build(output: Path) -> int:
    output.mkdir(parents=True, exist_ok=True)
    entries = []
    files = sorted(p for p in SOURCES.rglob("*") if p.is_file() and p.suffix in EXTENSIONS)
    for path in files:
        relative = path.relative_to(SOURCES)
        source = path.read_bytes()
        metadata = json.loads(parse(source, "--metadata"))
        rendered = parse(source, "--html")
        target = output / "lib" / relative.with_suffix(".html")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        entries.append((metadata["name"], metadata["description"], target.relative_to(output).as_posix()))
        print(f"[HTML] {relative} -> {target.relative_to(output)}", flush=True)

    entries.sort(key=lambda item: (item[0].casefold(), item[2]))
    listing = []
    for name, description, href in entries:
        listing.append(
            f'<li><a href="{escape(href, quote=True)}">{escape(name)}</a>'
            f'<span>{escape(description)}</span></li>'
        )
    index = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Library_Cpp</title>
<style>
:root{color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:#fff;color:#20242a;font-family:system-ui,-apple-system,'Yu Gothic',Meiryo,sans-serif}
main{max-width:800px;margin:0 auto;padding:32px 24px}
h1{font-size:25px;margin:0 0 20px}
ul{list-style:none;margin:0;padding:0}
li{border-top:1px solid #d6dce4;padding:13px 0}
a{font-weight:700;color:#25517c;text-decoration:none}
a:hover{text-decoration:underline}
span{display:block;margin-top:4px;font-size:13px;color:#4d5866}
@media print{main{padding:0}a{color:#20242a}li{break-inside:avoid}}
</style>
</head>
<body><main><h1>Library_Cpp</h1><ul>
""" + "\n".join(listing) + """
</ul></main></body></html>
"""
    (output / "index.html").write_text(index, encoding="utf-8")
    print(f"[HTML] index.html: {len(entries)} libraries", flush=True)
    return len(entries)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    build(args.output)


if __name__ == "__main__":
    main()
