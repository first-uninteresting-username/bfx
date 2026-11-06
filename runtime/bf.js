/*
 * bf.js: Brainfuck interpreter for the browser, plus the island bridge.
 *
 * Semantics are identical to tools/bf.py:
 *   - 65,536 cells, 8-bit, wrapping, pointer starts at 0.
 *   - Moving the pointer outside the tape throws BFError with the position.
 *   - '.' appends one raw byte to the output buffer.
 *   - Brackets are matched before execution. Unmatched brackets throw BFError.
 *   - Other bytes are comments.
 *
 * Island difference: ',' with no waiting input PAUSES the machine (run()
 * returns "input") instead of setting the cell to 0. feed(byte) queues an
 * input byte; the next run() resumes and that ',' returns the byte.
 *
 * Island bridge (only when a DOM exists):
 *   - finds every <bf-island src="..."> element, fetches the source and runs it;
 *   - after each pause sets the island's innerHTML to the output since the last
 *     pause (UTF-8 decoded), then clears the output buffer;
 *   - clicks on [data-ev="N"] inside the island queue byte N (event delegation);
 *   - when the program ends, the final output is shown and the island stops;
 *   - a step limit of 10,000,000 instructions per resume; errors are shown
 *     inline in the island.
 */
(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  } else {
    root.BF = api;
    if (typeof document !== "undefined") {
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
          api.mountIslands(document);
        });
      } else {
        api.mountIslands(document);
      }
    }
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var TAPE_SIZE = 65536;
  var STEP_LIMIT = 10000000;

  function BFError(message) {
    this.name = "BFError";
    this.message = message;
  }
  BFError.prototype = Object.create(Error.prototype);
  BFError.prototype.constructor = BFError;

  // Keep only the eight command characters; return an array of char codes.
  function compile(program) {
    var src = typeof program === "string" ? program : new TextDecoder().decode(program);
    var code = [];
    for (var i = 0; i < src.length; i++) {
      var ch = src.charAt(i);
      if ("+-<>[],.".indexOf(ch) >= 0) code.push(ch);
    }
    var jump = new Array(code.length).fill(0);
    var stack = [];
    for (var k = 0; k < code.length; k++) {
      if (code[k] === "[") {
        stack.push(k);
      } else if (code[k] === "]") {
        if (stack.length === 0) throw new BFError("unmatched ']' at instruction " + k);
        var open = stack.pop();
        jump[k] = open;
        jump[open] = k;
      }
    }
    if (stack.length > 0) {
      throw new BFError("unmatched '[' at instruction " + stack[stack.length - 1]);
    }
    return { code: code, jump: jump };
  }

  function Machine(program) {
    var c = compile(program);
    this.code = c.code;
    this.jump = c.jump;
    this.tape = new Uint8Array(TAPE_SIZE);
    this.ptr = 0;
    this.pc = 0;
    this.steps = 0;
    this.output = [];
    this.inputQueue = [];
    this.done = false;
  }

  // Queue one input byte for the next ','.
  Machine.prototype.feed = function (byte) {
    this.inputQueue.push(byte & 0xff);
  };

  // Execute until the program ends ("done"), reaches a ',' with no queued
  // input ("input"), or exhausts maxSteps (throws BFError).
  Machine.prototype.run = function (maxSteps) {
    if (maxSteps === undefined) maxSteps = STEP_LIMIT;
    var code = this.code, jump = this.jump, tape = this.tape;
    var ptr = this.ptr, pc = this.pc, steps = 0;
    var n = code.length;
    try {
      while (pc < n) {
        var c = code[pc];
        steps++;
        if (steps > maxSteps) {
          throw new BFError("step limit " + maxSteps + " exceeded at instruction " + pc);
        }
        switch (c) {
          case "+": tape[ptr] = (tape[ptr] + 1) & 0xff; break;
          case "-": tape[ptr] = (tape[ptr] - 1) & 0xff; break;
          case ">":
            ptr++;
            if (ptr >= TAPE_SIZE) throw new BFError("pointer moved past end of tape at instruction " + pc);
            break;
          case "<":
            ptr--;
            if (ptr < 0) throw new BFError("pointer moved before start of tape at instruction " + pc);
            break;
          case "[": if (tape[ptr] === 0) pc = jump[pc]; break;
          case "]": if (tape[ptr] !== 0) pc = jump[pc]; break;
          case ".": this.output.push(tape[ptr]); break;
          case ",":
            if (this.inputQueue.length === 0) {
              // Pause: pc stays on this ',' so the next run() re-executes it.
              return "input";
            }
            tape[ptr] = this.inputQueue.shift();
            break;
        }
        pc++;
      }
      this.done = true;
      return "done";
    } finally {
      // Save state on every exit path (pause, done, or thrown error).
      this.ptr = ptr;
      this.pc = pc;
      this.steps += steps;
    }
  };

  // Return and clear the output bytes produced since the last call.
  Machine.prototype.takeOutput = function () {
    var out = this.output;
    this.output = [];
    return new Uint8Array(out);
  };

  // Build-time style run: ',' at end of input yields 0. Returns output bytes.
  function runToEnd(program, input, maxSteps) {
    var m = new Machine(program);
    var pos = 0;
    var data = input || new Uint8Array(0);
    // Feed input lazily: queue one byte at a time when the machine pauses.
    for (;;) {
      if (m.run(maxSteps) === "done") break;
      if (pos < data.length) {
        m.feed(data[pos++]);
      } else {
        // EOF: the pending ',' must read 0. Queue a 0 and continue.
        m.feed(0);
      }
    }
    return m.takeOutput();
  }

  // ---- island bridge -------------------------------------------------------

  function escapeText(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function showError(el, err) {
    el.textContent = "";
    var box = el.ownerDocument.createElement("div");
    box.className = "bf-error";
    box.textContent = "bf island error: " + (err && err.message ? err.message : String(err));
    el.appendChild(box);
  }

  function mountIsland(el) {
    var src = el.getAttribute("src");
    if (!src) return;
    var state = { machine: null, stopped: false };

    function render(bytes) {
      el.innerHTML = new TextDecoder("utf-8").decode(bytes);
    }

    function resume(fn) {
      if (state.stopped) return;
      try {
        var status = fn();
        if (status === "done") {
          state.stopped = true;
          render(state.machine.takeOutput());
        } else {
          render(state.machine.takeOutput());
        }
      } catch (err) {
        state.stopped = true;
        showError(el, err);
      }
    }

    el.addEventListener("click", function (ev) {
      if (state.stopped || !state.machine) return;
      var target = ev.target;
      while (target && target !== el && !(target.hasAttribute && target.hasAttribute("data-ev"))) {
        target = target.parentNode;
      }
      if (!target || target === el) return;
      var n = parseInt(target.getAttribute("data-ev"), 10);
      if (!(n >= 1 && n <= 255)) return;
      state.machine.feed(n);
      resume(function () { return state.machine.run(); });
    });

    fetch(src).then(function (r) {
      if (!r.ok) throw new BFError("could not fetch " + src + " (" + r.status + ")");
      return r.text();
    }).then(function (text) {
      state.machine = new Machine(text);
      resume(function () { return state.machine.run(); });
    }).catch(function (err) {
      state.stopped = true;
      showError(el, err);
    });
  }

  function mountIslands(doc) {
    var list = doc.querySelectorAll("bf-island[src]");
    for (var i = 0; i < list.length; i++) mountIsland(list[i]);
  }

  return {
    BFError: BFError,
    Machine: Machine,
    compile: compile,
    runToEnd: runToEnd,
    mountIslands: mountIslands,
    escapeText: escapeText,
    STEP_LIMIT: STEP_LIMIT
  };
});
