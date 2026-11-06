#!/usr/bin/env python3
"""bfx build tests: exact output tree and bytes for the example site, and build errors."""
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DIST = os.path.join(ROOT, "dist")
EXPECTED_FILES = {
    "index.html",
    os.path.join("about", "index.html"),
    os.path.join("islands", "index.html"),
    os.path.join("islands", "counter.bf"),
    os.path.join("islands", "toggle.bf"),
    os.path.join("runtime", "bf.js"),
}
EXPECTED_INDEX = (
    b'<!doctype html><html><head><meta charset="utf-8"><title>bfx</title></head><body><h1>bfx</h1>\n'
    b'<div class="card"><h2>Hello from Brainfuck</h2></div>\n'
    b'<p><a href="/about/">About this site</a> and <a href="/islands/">the islands</a>.</p>\n'
    b'<script src="/runtime/bf.js"></script></body></html>'
)


def run_build(root):
    return subprocess.run([sys.executable, os.path.join(root, "bfx.py"), "build"],
                          capture_output=True, cwd=root, timeout=900)


def tree(root):
    found = set()
    for dirpath, _, names in os.walk(os.path.join(root, "dist")):
        for n in names:
            found.add(os.path.relpath(os.path.join(dirpath, n), os.path.join(root, "dist")))
    return found


def check_example_site():
    r = run_build(ROOT)
    assert r.returncode == 0, r.stderr.decode()
    assert tree(ROOT) == EXPECTED_FILES, sorted(tree(ROOT))
    with open(os.path.join(DIST, "index.html"), "rb") as f:
        assert f.read() == EXPECTED_INDEX, "index.html bytes differ"
    assert filecmp.cmp(os.path.join(ROOT, "islands", "counter.bf"), os.path.join(DIST, "islands", "counter.bf"), False)
    assert filecmp.cmp(os.path.join(ROOT, "islands", "toggle.bf"), os.path.join(DIST, "islands", "toggle.bf"), False)
    assert filecmp.cmp(os.path.join(ROOT, "runtime", "bf.js"), os.path.join(DIST, "runtime", "bf.js"), False)
    return "example site builds to the expected tree with the expected index bytes"


def check_build_errors():
    tmp = tempfile.mkdtemp(prefix="bfx-test-")
    try:
        for name in ("bfx.py", "components.bfc"):
            shutil.copy(os.path.join(ROOT, name), os.path.join(tmp, name))
        for folder in ("core", "tools", "pages", "islands", "runtime"):
            shutil.copytree(os.path.join(ROOT, folder), os.path.join(tmp, folder))
        with open(os.path.join(tmp, "pages", "index.page"), "wb") as f:
            f.write(b"no layout line here\n")
        r = run_build(tmp)
        assert r.returncode == 1 and b"#layout" in r.stderr, r.stderr.decode()
        with open(os.path.join(tmp, "pages", "index.page"), "wb") as f:
            f.write(b"#layout Base\nok\x00\n")
        r = run_build(tmp)
        assert r.returncode == 1 and b"zero byte" in r.stderr, r.stderr.decode()
    finally:
        shutil.rmtree(tmp)
    return "build rejects a page without a layout line and a page with a zero byte"


def main():
    failures = 0
    for check in (check_example_site, check_build_errors):
        try:
            print("PASS", check())
        except AssertionError as e:
            failures += 1
            print("FAIL", check.__name__, e)
    print("build tests: 2 run, %d failed" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
