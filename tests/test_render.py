#!/usr/bin/env python3
"""Render tests. Each case feeds components.bfc style text and a page through the
joined core program (the same join bfx.py uses) and compares exact output bytes.
The expected bytes are written out by hand in this file.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import bf  # noqa: E402


def joined_program():
    with open(os.path.join(ROOT, "core", "ORDER.txt")) as f:
        names = [line.strip() for line in f if line.strip()]
    parts = []
    for name in names:
        with open(os.path.join(ROOT, "core", name), "rb") as f:
            parts.append(f.read())
    return b"\n".join(parts)


PROGRAM = joined_program()

BASE_COMP = b'@Card\n<div class="card">$</div>\n@@\n@Base\n<html>$</html>\n@@\n'


def render(components, page):
    return bf.run(PROGRAM, components + b"\x00" + page, max_steps=4_000_000_000)


def big_page():
    """A page of more than twenty kilobytes with escapes, HTML characters, UTF-8 and components."""
    page = ["#layout Base\n"]
    expect = ["<html>"]
    i = 0
    size = 0
    while size < 21 * 1024:
        line = "Line %d: <>[]+-.,é \U0001F600 @@ x\n" % i
        page.append(line)
        expect.append(line.replace("@@", "@"))
        if i % 25 == 0:
            page.append("@Card(%d)\n" % i)
            expect.append('<div class="card">%d</div>\n' % i)
        size = sum(len(p.encode("utf-8")) for p in page)
        i += 1
    expect.append("</html>")
    return "".join(page).encode("utf-8"), "".join(expect).encode("utf-8")


CASES = [
    # name, components, page, expected output
    ("plain text passthrough", BASE_COMP, b"#layout Base\njust text here\n", b"<html>just text here\n</html>"),
    ("one component", BASE_COMP, b"#layout Base\n@Card(hi)\n", b'<html><div class="card">hi</div>\n</html>'),
    ("several components on one line", BASE_COMP,
     b"#layout Base\n@Card(a) and @Card(b)\n", b'<html><div class="card">a</div> and <div class="card">b</div>\n</html>'),
    ("unknown component", BASE_COMP, b"#layout Base\n@Nope(x)!\n", b"<html><!-- bfx: unknown component Nope -->!\n</html>"),
    ("at sign escape", BASE_COMP, b"#layout Base\na@@b\n", b"<html>a@b\n</html>"),
    ("page with no components", BASE_COMP, b"#layout Base\nno tags at all\n", b"<html>no tags at all\n</html>"),
    ("empty argument", BASE_COMP, b"#layout Base\n@Card()\n", b'<html><div class="card"></div>\n</html>'),
    ("html characters pass through", BASE_COMP, b"#layout Base\n<>[]+-.,<b>\n", b"<html><>[]+-.,<b>\n</html>"),
    ("utf-8 pass through", BASE_COMP, "#layout Base\nhéllo \U0001F600\n".encode("utf-8"),
     "<html>héllo \U0001F600\n</html>".encode("utf-8")),
    ("layout name not found", BASE_COMP, b"#layout Nope\nplain\n", b"<!-- bfx: unknown layout Nope -->plain\n"),
    ("at sign followed by space is literal", BASE_COMP, b"#layout Base\n@Card x\n", b"<html>@Card x\n</html>"),
    ("at sign at end of input", BASE_COMP, b"#layout Base\ntrail@", b"<html>trail@</html>"),
    ("at sign before open paren is literal", BASE_COMP, b"#layout Base\n@(x)\n", b"<html>@(x)\n</html>"),
    ("unterminated argument ends at input end", BASE_COMP, b"#layout Base\n@Card(hi",
     b'<html><div class="card">hi</div></html>'),
    ("empty body component", b"@Empty\n@@\n@Base\n<html>$</html>\n@@\n", b"#layout Base\n@Empty(x)|\n",
     b"<html>|\n</html>"),
    ("body without dollar sign drops the argument", b"@Plain\n<b>text</b>\n@@\n@Base\n<html>$</html>\n@@\n",
     b"#layout Base\n@Plain(zz)!\n", b"<html><b>text</b>!\n</html>"),
    ("layout without dollar sign", b"@Bare\n<head>x</head>\n@@\n", b"#layout Bare\nbody\n",
     b"<head>x</head>body\n"),
    ("duplicate component names are reported", b"@Base\n<html>$</html>\n@@\n@Card\nX$\n@@\n@Card\nY$\n@@\n",
     b"#layout Base\n@Card(z)\n", b"<html><!-- bfx: duplicate component Card -->\n</html>"),
    ("duplicate layout names are reported", b"@Base\n<a>$</a>\n@@\n@Base\n<b>$</b>\n@@\n",
     b"#layout Base\nhi\n", b"<!-- bfx: duplicate layout Base -->hi\n"),
]


def main():
    failures = 0
    for name, comp, page, want in CASES:
        t0 = time.time()
        got = render(comp, page)
        ok = got == want
        failures += not ok
        print("PASS" if ok else "FAIL", name, "(%.1f s)" % (time.time() - t0), flush=True)
        if not ok:
            print("   want:", want[:300], flush=True)
            print("   got: ", got[:300], flush=True)
    page, want = big_page()
    t0 = time.time()
    got = render(BASE_COMP, page)
    ok = got == want and len(page) >= 20 * 1024
    failures += not ok
    print("PASS" if ok else "FAIL", "page of %d bytes (%.1f s)" % (len(page), time.time() - t0), flush=True)
    if not ok:
        print("   want length", len(want), "got length", len(got), flush=True)
        for i, (a, b) in enumerate(zip(got, want)):
            if a != b:
                print("   first difference at byte", i, flush=True)
                break
    print("render tests: %d cases, %d failed" % (len(CASES) + 1, failures), flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
