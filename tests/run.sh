#!/usr/bin/env bash
# Runs every bfx test. Exits non-zero on the first failing suite.
set -euo pipefail
cd "$(dirname "$0")/.."

node_run() {
  if command -v node >/dev/null 2>&1; then
    node "$@"
  else
    nix shell nixpkgs#nodejs -c node "$@"
  fi
}

echo "== interpreter, python (tests/interp_cases.json)"
python3 tests/test_interp.py
echo "== interpreter, node (same cases)"
node_run tests/interp_test.js
echo "== islands through the runtime step function, node"
node_run tests/island_test.js
echo "== module harness tests"
python3 tests/test_modules.py
echo "== render tests (exact bytes)"
python3 tests/test_render.py
echo "== comment rule"
python3 tests/test_comments.py
echo "== build the example site"
python3 tests/test_build.py
echo "ALL TESTS PASSED"
