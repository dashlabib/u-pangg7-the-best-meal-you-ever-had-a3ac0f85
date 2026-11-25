#!/usr/bin/env python3
"""Publish the one-sentence entry for the make.fun bounty
"The Best Meal You Ever Had".

The entry lives in the ``ENTRY`` constant below and in ``entry.txt``
next to this file. This program validates it against the bounty gate
(UTF-8 text, a single line, 1 to 200 characters, not only white
space), writes the exact text to ``entry.txt`` in the output
directory, and reads it back to confirm the published bytes match.
Standard library only: no network access, no clock reads, no
randomness, so two runs always produce identical output.

The output directory is ``$MAKEFUN_OUTPUT_DIR`` when set, else
``/output``. Pass ``--check-only`` to validate without writing, or
``--self-test`` to exercise the validators against known-good and
known-bad inputs.
"""

import argparse
import os
import sys
from pathlib import Path

MAX_CHARS = 200

ENTRY = (
    "I never tasted it, but my grandmother's kitchen still finds me "
    "\u2014 ghee and fried onions through the wall, biryani passed "
    "through the doorway, steam blooming on the window as she called me in."
)


def validate_length(text: str) -> None:
    if len(text) < 1 or len(text) > MAX_CHARS:
        raise ValueError(
            f"entry is {len(text)} characters, outside the 1-{MAX_CHARS} range"
        )


def validate_not_blank(text: str) -> None:
    if not text or text.isspace():
        raise ValueError("entry is empty or only white space")


def validate_single_line(text: str) -> None:
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")


def validate(text: str) -> None:
    validate_not_blank(text)
    validate_length(text)
    validate_single_line(text)


def write_entry(text: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "entry.txt"
    out_path.write_text(text, encoding="utf-8")
    return out_path


def read_back(out_path: Path) -> str:
    return out_path.read_text(encoding="utf-8")


def self_test() -> int:
    failures = []

    def check(name: str, ok: bool) -> None:
        if not ok:
            failures.append(name)
        print(f"{'PASS' if ok else 'FAIL'}: {name}")

    # Known-good: the entry itself passes every validator.
    try:
        validate(ENTRY)
        check("entry passes all validators", True)
    except ValueError:
        check("entry passes all validators", False)

    # Known-bad: empty, blank-only, too long, multi-line.
    for name, bad in (
        ("empty rejected", ""),
        ("blank-only rejected", "   "),
        ("over-limit rejected", "x" * (MAX_CHARS + 1)),
        ("multi-line rejected", "one line\ntwo lines"),
    ):
        try:
            validate(bad)
            check(name, False)
        except ValueError:
            check(name, True)

    # Known-good boundaries: 1 char and exactly 200 chars pass.
    for name, good in (
        ("one char accepted", "a"),
        ("200 chars accepted", "b" * MAX_CHARS),
    ):
        try:
            validate(good)
            check(name, True)
        except ValueError:
            check(name, False)

    if failures:
        print(f"self-test FAILED: {len(failures)} check(s) failed")
        return 1
    print("self-test passed")
    return 0


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-only", action="store_true",
        help="validate the entry without writing it",
    )
    parser.add_argument(
        "--self-test", action="store_true",
        help="run the validator self-test and exit",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.self_test:
        return self_test()
    validate(ENTRY)
    if args.check_only:
        print(f"Valid: {len(ENTRY)} characters")
        return 0
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_path = write_entry(ENTRY, out_dir)
    # Copy beside main.py so the repo entry matches the published bytes.
    here = Path(__file__).resolve().parent
    local_path = write_entry(ENTRY, here)
    published = read_back(out_path)
    local = read_back(local_path)
    if published != ENTRY or local != ENTRY:
        raise SystemExit("published entry does not match ENTRY")
    print(f"Wrote {len(ENTRY)} characters to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
