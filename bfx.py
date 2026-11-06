#!/usr/bin/env python3
"""bfx: a small static site builder whose page work is done in Brainfuck.

Usage:
  python3 bfx.py build    render every page into dist/
  python3 bfx.py dev      build, then rebuild on change and serve dist/ on port 8000

Host code here only reads and writes bytes and files. All page work (template
lookup, argument substitution, layout, escaping) runs in core/ as Brainfuck.
The build interpreter is tools/bf.py.
"""

import http.server
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import bf  # noqa: E402

CORE = os.path.join(ROOT, "core")
PAGES = os.path.join(ROOT, "pages")
ISLANDS = os.path.join(ROOT, "islands")
RUNTIME = os.path.join(ROOT, "runtime")
COMPONENTS = os.path.join(ROOT, "components.bfc")
DIST = os.path.join(ROOT, "dist")

# The loader stores one fifteen cell element per component byte starting at cell 75.
# Sweeps look two elements past the last one, so a component file this long still fits the tape.
MAX_COMPONENT_BYTES = 4000


class BuildError(Exception):
    pass


def load_program():
    """Join the core modules in the order given by core/ORDER.txt."""
    with open(os.path.join(CORE, "ORDER.txt")) as f:
        names = [line.strip() for line in f if line.strip()]
    parts = []
    for name in names:
        with open(os.path.join(CORE, name), "rb") as f:
            parts.append(f.read())
    return b"\n".join(parts)


def read_components():
    with open(COMPONENTS, "rb") as f:
        data = f.read()
    if b"\x00" in data:
        raise BuildError("components.bfc contains a zero byte")
    if len(data) > MAX_COMPONENT_BYTES:
        raise BuildError("components.bfc is %d bytes; the limit is %d" % (len(data), MAX_COMPONENT_BYTES))
    return data


def output_path(page_file):
    name = os.path.splitext(os.path.basename(page_file))[0]
    if name == "index":
        return os.path.join(DIST, "index.html")
    return os.path.join(DIST, name, "index.html")


def render_page(program, components, page_file):
    with open(page_file, "rb") as f:
        page = f.read()
    if b"\x00" in page:
        raise BuildError("%s contains a zero byte" % page_file)
    if not page.startswith(b"#layout "):
        raise BuildError("%s must start with a '#layout Name' line" % page_file)
    return bf.run(program, components + b"\x00" + page)


def copy_assets():
    islands_out = os.path.join(DIST, "islands")
    os.makedirs(islands_out, exist_ok=True)
    for name in sorted(os.listdir(ISLANDS)):
        if name.endswith(".bf"):
            shutil.copyfile(os.path.join(ISLANDS, name), os.path.join(islands_out, name))
    runtime_out = os.path.join(DIST, "runtime")
    os.makedirs(runtime_out, exist_ok=True)
    shutil.copyfile(os.path.join(RUNTIME, "bf.js"), os.path.join(runtime_out, "bf.js"))


def build():
    program = load_program()
    components = read_components()
    pages = sorted(os.path.join(PAGES, n) for n in os.listdir(PAGES) if n.endswith(".page"))
    if not pages:
        raise BuildError("no pages found in pages/")
    os.makedirs(DIST, exist_ok=True)
    written = []
    for page_file in pages:
        out = render_page(program, components, page_file)
        path = output_path(page_file)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(out)
        written.append(os.path.relpath(path, ROOT))
    copy_assets()
    return written


def watched_files():
    files = [COMPONENTS]
    for folder in (PAGES, ISLANDS, RUNTIME, CORE):
        for name in os.listdir(folder):
            files.append(os.path.join(folder, name))
    return [f for f in files if os.path.isfile(f)]


def snapshot():
    state = {}
    for f in watched_files():
        try:
            state[f] = os.stat(f).st_mtime_ns
        except OSError:
            pass
    return state


def dev(port=8000):
    try:
        for rel in build():
            print("built", rel, flush=True)
    except BuildError as e:
        print("build error:", e, flush=True)
    server = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--directory", DIST])
    print("serving dist/ at http://localhost:%d/" % port, flush=True)
    seen = snapshot()
    try:
        while True:
            time.sleep(0.5)
            now = snapshot()
            if now != seen:
                seen = now
                try:
                    print("change detected; rebuilding", flush=True)
                    for rel in build():
                        print("built", rel, flush=True)
                except BuildError as e:
                    print("build error:", e, flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        server.terminate()
    return 0


def main(argv):
    if len(argv) != 1 or argv[0] not in ("build", "dev"):
        sys.stderr.write(__doc__)
        return 2
    if argv[0] == "build":
        try:
            for rel in build():
                print("built", rel)
        except BuildError as e:
            sys.stderr.write("build error: %s\n" % e)
            return 1
        return 0
    return dev()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
