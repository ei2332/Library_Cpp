#!/usr/bin/env python3
"""Verify published source URLs and all libparser @check cases."""

import os
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
            download = ["oj", "download", "--silent", "-d", str(tests)]
            system = parts.hostname == "judge.yosupo.jp"
            if system:
                download.append("--system")
            download.append(url)
            subprocess.run(download, check=True, timeout=600 if system else 120)
            inputs = list(tests.rglob("*.in"))
            if not inputs or any(not p.with_suffix(".out").is_file() for p in inputs):
                raise ValueError(f"@check #{index}: no complete test cases downloaded")
            subprocess.run(
                ["oj", "test", "-d", str(tests), "-c", str(executable)],
                check=True,
                timeout=120,
            )
            print(f"[OK] {relative}: @check #{index}", flush=True)


def select_paths(paths: list[Path]) -> list[Path]:
    base = os.environ.get("VERIFY_BASE_SHA", "")
    if not base or base == "0" * 40:
        print("[INFO] No comparison commit; verifying all sources.", flush=True)
        return paths

    diff = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMRD", "-z", base, "HEAD"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    changed = set(filter(None, diff.stdout.decode("utf-8").split(chr(0))))
    if any(name.startswith("scripts/") or name.startswith(".github/workflows/") for name in changed):
        print("[INFO] Verification infrastructure changed; verifying all sources.", flush=True)
        return paths

    selected = [path for path in paths if path.relative_to(ROOT).as_posix() in changed]
    print(f"[INFO] Changed sources: {len(selected)} of {len(paths)}.", flush=True)
    return selected


def main() -> int:
    paths = sorted(path for path in SOURCES.rglob("*") if path.is_file() and path.suffix in {".cpp", ".hpp", ".h", ".cc", ".cxx"})
    if not paths:
        print(f"[FAIL] no source files under {SOURCES}", file=sys.stderr)
        return 1
    paths = select_paths(paths)
    if not paths:
        print("[SKIP] No source files to verify.", flush=True)
        return 0
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
