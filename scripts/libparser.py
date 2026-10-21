
import sys
import os
import shlex
import argparse
import subprocess

# ===== グローバル変数 =====

text = ""
scopes = []
checks = []
checked = []

library_name = None
reference_url = None
license_info = None
description = None

active_scope = None
single_scope = False
defined_scopes = set()


# ===== 共通処理 =====

def Argc(tag, args, low, high=None):
    if len(args) < low or (high is not None and len(args) > high):
        raise ValueError(f"{tag}: invalid argument count")


# ===== コマンド処理 =====

def _name(args):
    global library_name
    Argc("@name", args, 1, 1)
    if library_name is not None:
        raise ValueError("duplicate @name")
    library_name = args[0]
    return False


def _url(args):
    global reference_url
    Argc("@url", args, 1, 1)
    if reference_url is not None:
        raise ValueError("duplicate @url")
    if not args[0]:
        raise ValueError("empty URL")
    reference_url = args[0]
    return True


def _license(args):
    global license_info
    Argc("@license", args, 1, 1)
    if license_info is not None:
        raise ValueError("duplicate @license")
    if not args[0]:
        raise ValueError("empty license")
    license_info = args[0]
    return True


def _global_expl(args):
    global description
    Argc("@expl", args, 1)
    if description is not None:
        raise ValueError("duplicate @expl")
    description = args
    return False


def _check(args):
    Argc("@check", args, 1)
    if not args[0]:
        raise ValueError("empty URL")
    checks.append((args[0], args[1:]))
    return False


def _checked(args):
    Argc("@checked", args, 1)
    if not args[0]:
        raise ValueError("empty URL")
    checked.append((args[0], args[1:]))
    return False


def _expl(args):
    Argc("expl", args, 1)
    return True


def _comp(args):
    Argc("comp", args, 1)
    return True


def _text(args):
    Argc("text", args, 0)
    return True


def _start(args):
    global active_scope, single_scope
    Argc("!", args, 1, 1)
    if active_scope is not None:
        raise ValueError("nested scope")
    if not args[0]:
        raise ValueError("empty scope name")

    active_scope = args[0]
    single_scope = False
    defined_scopes.add(active_scope)
    return False


def _start_single(args):
    global single_scope
    _start(args)
    single_scope = True
    return False


def _end(args):
    global active_scope
    Argc("end", args, 0, 0)
    if active_scope is None or single_scope:
        raise ValueError("unexpected end")
    active_scope = None
    return False


COMMANDS = {
    "@name": _name,
    "@url": _url,
    "@license": _license,
    "@expl": _global_expl,
    "@check": _check,
    "@checked": _checked,
    "expl": _expl,
    "comp": _comp,
    "text": _text,
    "!": _start,
    "!!": _start_single,
    "end": _end,
}


# ===== スコープ処理 =====

def ScopeVisible() -> bool:
    return active_scope is None or active_scope in scopes


def ScopeNext(target: bool) -> None:
    global active_scope, single_scope
    if target:
        active_scope = None
        single_scope = False


def ScopeValidate() -> None:
    if active_scope is not None:
        if single_scope:
            raise ValueError("missing line after !!")
        raise ValueError(f"unclosed scope: {active_scope}")

    unknown = set(scopes) - defined_scopes
    if unknown:
        raise ValueError(f"undefined scope: {sorted(unknown)}")


# ===== パーサ =====

def Parse() -> str:
    result = []

    for n, line in enumerate(text.splitlines(keepends=True), 1):
        target = single_scope
        visible = True

        try:
            s = line.lstrip(" \t")
            if s.startswith("////"):
                tokens = shlex.split(s[4:])

                if not tokens:
                    raise ValueError("empty command")

                tag, *args = tokens

                if tag not in COMMANDS:
                    raise ValueError(f"unknown command: {tag}")

                visible = COMMANDS[tag](args)

            if visible and ScopeVisible():
                result.append(line)

            ScopeNext(target)

        except ValueError as e:
            raise ValueError(f"line {n}: {e}") from e

    try:
        ScopeValidate()
    except ValueError as e:
        raise ValueError(
            f"line {n if text else 1}: {e}"
        ) from e

    return "".join(result)


# ===== 再実行 =====

def Rerun(url, flags):
    cmd = [sys.executable, os.path.abspath(__file__)]
    cmd += [f"-s={flag}" for flag in flags]

    p = subprocess.run(
        cmd,
        input=text.encode("utf-8"),
        capture_output=True
    )

    if p.returncode != 0:
        sys.stderr.buffer.write(p.stderr)
        sys.exit(p.returncode)

    sys.stdout.buffer.write(p.stdout)
    sys.stderr.buffer.write(url.encode("utf-8") + b"\n")


# ===== メイン処理 =====

def main():
    global text, scopes

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument("-s", action="append", default=[])
    group.add_argument("-c", nargs="?", action="append", const="")
    group.add_argument("-u", action="store_true")

    args = parser.parse_args()

    check = -1
    if args.c is not None:
        if len(args.c) != 1:
            parser.error("-c cannot be repeated")

        if args.c[0] != "":
            try:
                check = int(args.c[0])
                if check <= 0:
                    raise ValueError
            except ValueError:
                parser.error("-c requires a positive integer")

    scopes = args.s

    try:
        text = sys.stdin.buffer.read().decode("utf-8")
        parseStr = Parse()

        if args.u:
            if reference_url is None:
                raise ValueError("@url is not defined")
            print(reference_url)

        elif args.c is not None:
            if check == -1:
                print(len(checks))
            else:
                if check > len(checks):
                    raise ValueError("@check index out of range")
                Rerun(*checks[check - 1])

        else:
            sys.stdout.buffer.write(parseStr.encode("utf-8"))

    except (ValueError, UnicodeError) as e:
        sys.exit(f"libparse: {e}")


if __name__ == "__main__":
    main()
