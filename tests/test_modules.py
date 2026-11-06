#!/usr/bin/env python3
"""Module level harness tests for core/*.bf.

Each core module is run alone (after the loader where it needs a table) and the
tape is checked against values worked out from the module contracts.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import bf  # noqa: E402

CORE = os.path.join(ROOT, "core")
ELEM0 = 75
STRIDE = 15
LANE_CURSOR = 8
LANE_NAMEFIRST = 11
LANE_MARKER = 12
LANE_STORE = 13
STATUS = 74


def module(name):
    with open(os.path.join(CORE, name)) as f:
        return f.read()


def run(program_text, data):
    got = {}

    def trace(steps, tape):
        got["tape"] = bytes(tape)

    out = bf.run(program_text, data, max_steps=200_000_000, trace=trace)
    return out, got["tape"]


def elements(tape):
    rows = []
    base = ELEM0
    while tape[base + LANE_MARKER]:
        rows.append(base)
        base += STRIDE
    return rows


def cursor_elements(tape):
    return [i + 1 for i, b in enumerate(elements(tape)) if tape[b + LANE_CURSOR]]


COMPONENTS = b"@Card\n<div>$</div>\n@@\n"


def loader_program():
    return module("load_components.bf")


def to_sweep_start():
    return ">" * 64


def passes(query):
    text = ""
    for _ in query:
        text += "\n,\n" + module("find_pass.bf")
    return text


def test_loader():
    out, tape = run(loader_program(), COMPONENTS + b"\x00")
    rows = elements(tape)
    data = bytes(tape[b] for b in rows)
    assert data == COMPONENTS, data
    assert tape[ELEM0 + STRIDE * len(rows)] == 0 and tape[ELEM0 + STRIDE * len(rows) + LANE_MARKER] == 0
    assert tape[0] == 0, "loader must end on cell zero"
    # the name first flag is set only on the first byte of the name
    firsts = [i + 1 for i, b in enumerate(rows) if tape[b + LANE_NAMEFIRST]]
    assert firsts == [2, 21], firsts      # the header name and the first byte after the end line
    for b in rows:
        for lane in (1, 2, 3, 5, 6, 7, 8, 9, 10):
            assert tape[b + lane] == 0, ("work lane not clear", b, lane)
    return "loader: %d elements, name first flags %s" % (len(rows), firsts)


def test_reset_and_passes():
    text = loader_program() + to_sweep_start() + "\n" + module("find_reset.bf")
    _, tape = run(text, COMPONENTS + b"\x00")
    assert cursor_elements(tape) == [2, 21], cursor_elements(tape)   # every name first byte
    text += passes(b"Card")
    _, tape = run(text, COMPONENTS + b"\x00Card")
    assert cursor_elements(tape) == [6], cursor_elements(tape)   # the header newline
    _, tape = run(loader_program() + to_sweep_start() + "\n" + module("find_reset.bf")
                  + passes(b"Carx"), COMPONENTS + b"\x00Carx")
    assert cursor_elements(tape) == [], "a name that differs must leave no cursor"
    return "reset and pass: cursor after Card is on the header newline"


def test_clear_and_save_restore():
    text = loader_program() + to_sweep_start() + "\n" + module("find_reset.bf") + passes(b"Card")
    text_saved = text + "\n" + module("save_cursor.bf")
    _, tape = run(text_saved, COMPONENTS + b"\x00Card")
    assert cursor_elements(tape) == [], "save must clear the cursor"
    assert [i + 1 for i, b in enumerate(elements(tape)) if tape[b + LANE_STORE]] == [6]
    text_restored = text_saved + "\n" + module("restore_cursor.bf")
    _, tape = run(text_restored, COMPONENTS + b"\x00Card")
    assert cursor_elements(tape) == [6]
    text_cleared = text + "\n" + module("clear_cursor.bf")
    _, tape = run(text_cleared, COMPONENTS + b"\x00Card")
    assert cursor_elements(tape) == []
    return "save, restore and clear cursor sweeps behave as documented"


def emit_program(name_bytes, sweeps_normal, skip_first):
    text = loader_program() + to_sweep_start() + "\n" + module("find_reset.bf") + passes(name_bytes)
    if skip_first:
        text += "\n" + module("emit_skip.bf")
    for _ in range(sweeps_normal):
        text += "\n" + module("emit_normal.bf")
    return text


def test_emit_body():
    # skip past the header newline then write the body up to the dollar sign
    out, tape = run(emit_program(b"Card", 30, True), COMPONENTS + b"\x00Card")
    assert out == b"<div>", out
    assert tape[STATUS] >= 1, "pause status expected"
    # skip the dollar sign then write the rest of the body
    text = emit_program(b"Card", 30, True) + "\n" + module("emit_skip.bf")
    for _ in range(30):
        text += "\n" + module("emit_normal.bf")
    out, tape = run(text, COMPONENTS + b"\x00Card")
    assert out == b"<div></div>", out
    assert cursor_elements(tape) == []
    return "emit: body writes up to the dollar sign and then the rest"


def main():
    tests = [test_loader, test_reset_and_passes, test_clear_and_save_restore, test_emit_body]
    failures = 0
    for t in tests:
        try:
            print("PASS", t())
        except AssertionError as e:
            failures += 1
            print("FAIL", t.__name__, e)
    print("module tests: %d run, %d failed" % (len(tests), failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
