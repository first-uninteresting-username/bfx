# bfx

A small Astro-style static site builder. Pages are rendered by a Brainfuck
program. Interactive islands are Brainfuck programs that run in the browser.

## Layout

- `bfx.py` the command line. `build` renders `pages/` into `dist/`. `dev` rebuilds
  when a watched file changes and serves `dist/` with `python3 -m http.server`.
  Host code only moves bytes and files. It checks inputs and joins modules.
- `core/` the page renderer. `core/ORDER.txt` lists the modules in join order.
  `bfx.py` concatenates them and runs the result for each page.
- `tools/bf.py` the build-time Brainfuck interpreter (`--trace` prints a dump).
- `runtime/bf.js` the browser interpreter and the island bridge.
- `islands/*.bf` island programs, copied to `dist/islands/`.
- `components.bfc` component definitions. `pages/*.page` pages.
- `tests/` the test suite. Run it with `bash tests/run.sh`.

## Pages and components

`components.bfc`:

```
@Card
<div class="card"><h2>$</h2></div>
@@
```

A component starts with `@Name` (letters) on its own line. Its body is every line
up to a line that contains only `@@`. The body does not include the newline before
`@@`. `$` marks where the argument goes. A body holds at most one `$`.

A page starts with `#layout Name`. The rest of the page is copied through, except:

- `@Name(arg)` is replaced by the component body with `arg` in place of `$`.
- `@@` outputs a single `@`.
- An unknown component outputs `<!-- bfx: unknown component Name -->`.

Routing: `pages/index.page` becomes `dist/index.html`. `pages/about.page` becomes
`dist/about/index.html`.

## Islands

An island is `<bf-island src="/islands/counter.bf"></bf-island>`. The runtime
finds it, fetches the program, and runs it. The program's `,` pauses until a click
on an element with `data-ev="N"` queues byte `N`. After each pause the island's
HTML is replaced by the output since the previous pause. A program has a step
limit of 10 million instructions per resume.

## Running

```
python3 bfx.py build          # render into dist/
python3 bfx.py dev            # rebuild on change and serve on port 8000
bash tests/run.sh             # all tests
```

## Limits and behaviour notes

- `components.bfc` must not contain a zero byte and is limited to 4000 bytes
  (each byte takes a 15 cell element on the tape).
- Page files must not contain a zero byte and must start with `#layout `.
  The eight bytes of the `#layout ` prefix are skipped without being checked.
- Layout names and component names end at a space, a newline, an at sign, an open
  paren, or the end of the input. Other bytes, including non letters, are name bytes.
- Only the last 16 name bytes are kept for the unknown component comment. Longer
  names never match a component.
- An argument runs from after `(` to the first `)`. Arguments are not expanded and
  `@@` inside an argument is copied as is. An unterminated argument ends at the
  end of the input.
- A body line that starts with `@` is read as a component header by the lookup.
  Avoid it in component bodies.
- A component or layout whose name is defined twice produces a
  `duplicate` comment instead of output.
- A layout without `$` outputs its body and then the page. A component without `$`
  drops its argument. An empty component body outputs nothing.
- An unknown layout outputs `<!-- bfx: unknown layout Name -->` and then the page.
- Speed: rendering is slow in the Python interpreter. Each component use costs about
  one sweep over the component table for every name byte. The 21 KB test page takes
  about 20 seconds.
- Islands run in the browser. Their step limit is per resume, not per page.

## How the core was written

The core modules and the island programs are plain Brainfuck text. They were
written with scratch generators that expand repeated pointer moves and put comments
next to them. The generators are not part of this repository. The tests check the
behaviour of every module and of the joined program. `tests/test_comments.py`
checks that comments never contain command characters.
