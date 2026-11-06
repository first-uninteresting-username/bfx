#!/usr/bin/env python3
"""Runs tests/interp_cases.json through tools/bf.py. Exits non-zero on failure."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import bf  # noqa: E402

def main():
    with open(os.path.join(HERE, "interp_cases.json")) as f:
        cases = json.load(f)["cases"]
    failures = 0
    for case in cases:
        data = bytes.fromhex(case.get("input_hex", ""))
        try:
            got = bf.run(case["program"], data, max_steps=10_000_000)
            if "error_contains" in case:
                failures += 1
                print("FAIL (py)", case["name"], "expected error, got output", got.hex())
                continue
            want = bytes.fromhex(case["output_hex"])
            if got != want:
                failures += 1
                print("FAIL (py)", case["name"], "want", want.hex(), "got", got.hex())
        except bf.BFError as e:
            if "error_contains" in case and case["error_contains"] in str(e):
                continue
            failures += 1
            print("FAIL (py)", case["name"], "unexpected error:", e)
    print("py interp: %d cases, %d failed" % (len(cases), failures))
    failures += check_trace_flag()
    return 1 if failures else 0


def check_trace_flag():
    """--trace prints the instruction count and the first 64 cells to stderr."""
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".bf", delete=False) as f:
        f.write("+++[>++<-]>.")
        path = f.name
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "..", "tools", "bf.py"), "--trace", path],
                           capture_output=True)
    finally:
        os.unlink(path)
    ok = r.returncode == 0 and r.stdout == bytes([6]) and b"instructions:" in r.stderr and b"cells 0..63:" in r.stderr
    print("trace flag", "ok" if ok else "FAILED")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
