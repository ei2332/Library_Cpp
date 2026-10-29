#!/usr/bin/env python3
"""Verify published source URLs and all libparser @check cases."""

import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PARSER = ROOT / "scripts" / "libparser.py"
SOURCES = ROOT / "src"
REPOSITORY = "ei2332/Library_Cpp"
PUBLISHED_BRANCH = "main"


def parse(source: bytes, option: str) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        [sys.executable, str(PARSER), option],
        input=source,
        capture_output=True,
        check=False,
        timeout=60,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result


def verify_file(path: Path) -> None:
    relative = path.relative_to(ROOT).as_posix()
    source = path.read_bytes()
    expected = (
        f"https://github.com/{REPOSITORY}/blob/{PUBLISHED_BRANCH}/"
        f"{quote(relative, safe='/')}"
    )
    actual = parse(source, "-u").stdout.decode("utf-8").strip()
    if actual != expected:
        raise ValueError(f"@url mismatch: expected {expected!r}, got {actual!r}")
    print(f"[OK] {relative}: @url", flush=True)

    count = int(parse(source, "-c").stdout.decode("utf-8").strip())
    if count < 0:
        raise ValueError(f"negative @check count: {count}")

    for index in range(1, count + 1):
        parsed = parse(source, f"-c{index}")
        urls = parsed.stderr.decode("utf-8").strip().splitlines()
        if len(urls) != 1:
            raise ValueError(f"@check #{index}: expected one problem URL, got {urls!r}")
        url = urls[0]
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.hostname or parts.username or parts.password:
            raise ValueError(f"@check #{index}: invalid problem URL: {url!r}")

        with tempfile.TemporaryDirectory(prefix="library-check-") as directory:
            workspace = Path(directory)
            program = workspace / "main.cpp"
            executable = workspace / "main"
            tests = workspace / "test"
            program.write_bytes(parsed.stdout)

            print(f"[TEST] {relative}: @check #{index} ({url})", flush=True)
            subprocess.run(
                ["g++", "-std=c++20", "-O2", "-pipe", "-I", str(SOURCES), "-I", str(path.parent), str(program), "-o", str(executable)],
                check=True,
                timeout=120,
            )
            subprocess.run(["oj", "download", "-d", str(tests), url], check=True, timeout=120)
            inputs = list(tests.rglob("*.in"))
            if not inputs or any(not p.with_suffix(".out").is_file() for p in inputs):
                raise ValueError(f"@check #{index}: no complete test cases downloaded")
            subprocess.run(
                ["oj", "test", "-d", str(tests), "-c", str(executable)],
                check=True,
                timeout=120,
            )
            print(f"[OK] {relative}: @check #{index}", flush=True)


def main() -> int:
    paths = sorted(path for path in SOURCES.rglob("*") if path.is_file() and path.suffix in {".cpp", ".hpp", ".h", ".cc", ".cxx"})
    if not paths:
        print(f"[FAIL] no source files under {SOURCES}", file=sys.stderr)
        return 1
    failed = 0
    for path in paths:
        try:
            verify_file(path)
        except (OSError, UnicodeError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            print(f"[FAIL] {path.relative_to(ROOT)}: {exc}", file=sys.stderr)
            failed += 1
    print(f"Verified {len(paths)} file(s); {failed} failure(s).", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
