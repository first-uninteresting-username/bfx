#!/usr/bin/env python3
"""Every line of a Brainfuck module is either code (only command characters and
spaces) or a comment (no command characters at all). Mixed lines fail."""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
COMMANDS = set("+-<>[],.")


def check(path):
    problems = []
    with open(path) as f:
        for n, line in enumerate(f, 1):
            chars = set(line.rstrip("\n"))
            if chars & COMMANDS:
                extra = chars - COMMANDS - {" ", "\t"}
                if extra:
                    problems.append((n, line.rstrip("\n")[:70]))
    return problems


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "core", "*.bf")) + glob.glob(os.path.join(ROOT, "islands", "*.bf")))
    bad = 0
    for path in files:
        problems = check(path)
        bad += len(problems)
        for n, text in problems:
            print("comment mixed with code: %s line %d: %s" % (os.path.relpath(path, ROOT), n, text))
    print("comment check: %d files, %d mixed lines" % (len(files), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
