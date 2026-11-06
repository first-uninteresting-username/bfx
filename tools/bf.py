#!/usr/bin/env python3
"""Brainfuck interpreter for build time.

Semantics (shared with runtime/bf.js):
  - 65,536 cells, 8-bit, wrapping. Pointer starts at 0.
  - Moving the pointer outside the tape is a fatal error (reports position).
  - ',' at EOF sets the cell to 0.
  - '.' writes one raw byte.
  - Brackets are matched before execution. Unmatched brackets are an error.
  - Any other byte is a comment and is ignored.

CLI:  python3 tools/bf.py PROGRAM.bf [--input FILE] [--trace]
"""

import sys

TAPE_SIZE = 65536


class BFError(Exception):
    pass


def match_brackets(code):
    """Return a list where jump[i] is the matching bracket index for code[i]."""
    jump = [0] * len(code)
    stack = []
    for i, c in enumerate(code):
        if c == "[":
            stack.append(i)
        elif c == "]":
            if not stack:
                raise BFError("unmatched ']' at instruction %d" % i)
            j = stack.pop()
            jump[i] = j
            jump[j] = i
    if stack:
        raise BFError("unmatched '[' at instruction %d" % stack[-1])
    return jump


def run(program, data=b"", max_steps=None, trace=None):
    """Run a Brainfuck program.

    program: bytes or str. Only the eight command characters are kept.
    data: input bytes consumed by ','.
    max_steps: optional instruction budget (BFError when exceeded).
    trace: optional callable receiving (steps, tape) when the program ends.
    Returns the output bytes.
    """
    if isinstance(program, str):
        program = program.encode("utf-8")
    code = [chr(b) for b in program if chr(b) in "+-<>[],."]
    jump = match_brackets(code)

    tape = bytearray(TAPE_SIZE)
    ptr = 0
    pc = 0
    inp = 0
    out = bytearray()
    steps = 0
    n = len(code)

    while pc < n:
        c = code[pc]
        steps += 1
        if max_steps is not None and steps > max_steps:
            raise BFError("step limit %d exceeded at instruction %d" % (max_steps, pc))
        if c == "+":
            tape[ptr] = (tape[ptr] + 1) & 0xFF
        elif c == "-":
            tape[ptr] = (tape[ptr] - 1) & 0xFF
        elif c == ">":
            ptr += 1
            if ptr >= TAPE_SIZE:
                raise BFError("pointer moved past end of tape at instruction %d" % pc)
        elif c == "<":
            ptr -= 1
            if ptr < 0:
                raise BFError("pointer moved before start of tape at instruction %d" % pc)
        elif c == "[":
            if tape[ptr] == 0:
                pc = jump[pc]
        elif c == "]":
            if tape[ptr] != 0:
                pc = jump[pc]
        elif c == ".":
            out.append(tape[ptr])
        elif c == ",":
            if inp < len(data):
                tape[ptr] = data[inp]
                inp += 1
            else:
                tape[ptr] = 0
        pc += 1

    if trace is not None:
        trace(steps, tape)
    return bytes(out)


def _trace_to_stderr(steps, tape):
    sys.stderr.write("instructions: %d\n" % steps)
    sys.stderr.write("cells 0..63: " + " ".join("%d" % v for v in tape[:64]) + "\n")


def main(argv):
    args = list(argv)
    trace = "--trace" in args
    if trace:
        args.remove("--trace")
    input_path = None
    if "--input" in args:
        i = args.index("--input")
        input_path = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        sys.stderr.write("usage: bf.py PROGRAM.bf [--input FILE] [--trace]\n")
        return 2
    with open(args[0], "rb") as f:
        program = f.read()
    data = b""
    if input_path is not None:
        with open(input_path, "rb") as f:
            data = f.read()
    try:
        out = run(program, data, trace=_trace_to_stderr if trace else None)
    except BFError as e:
        sys.stderr.write("bf error: %s\n" % e)
        return 1
    sys.stdout.buffer.write(out)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
