// Runs islands/counter.bf and islands/toggle.bf through the runtime step
// function (no DOM) and checks the exact HTML after each event.
"use strict";
const fs = require("fs");
const path = require("path");
const BF = require(path.join(__dirname, "..", "runtime", "bf.js"));

const dec = (b) => new TextDecoder("utf-8").decode(b);
let failures = 0;

function check(label, got, want) {
  if (got !== want) {
    failures++;
    console.log("FAIL", label, "\n  want:", JSON.stringify(want), "\n  got: ", JSON.stringify(got));
  }
}

function counterHtml(n) {
  return '<button data-ev="1">-</button> <span>' + n + '</span> <button data-ev="2">+</button>';
}

function runSequence(file, events, htmlFor, label) {
  const m = new BF.Machine(fs.readFileSync(file, "utf8"));
  let status = m.run();
  check(label + " start status", status, "input");
  check(label + " start html", dec(m.takeOutput()), htmlFor(0));
  for (const ev of events.list) {
    m.feed(ev.byte);
    status = m.run();
    check(label + " after event " + ev.byte + " status", status, "input");
    check(label + " after event " + ev.byte, dec(m.takeOutput()), htmlFor(ev.state));
  }
}

// Counter: start, + x3, - x5 (wraps to 254).
const counterEvents = [];
let value = 0;
for (let i = 0; i < 3; i++) { value = (value + 1) & 255; counterEvents.push({ byte: 2, state: value }); }
for (let i = 0; i < 5; i++) { value = (value - 1) & 255; counterEvents.push({ byte: 1, state: value }); }
check("counter expected final value", value, 254);
runSequence(path.join(__dirname, "..", "islands", "counter.bf"), { list: counterEvents }, counterHtml, "counter");

// Counter: every value 0..255 reached by + (checks digit carries and wrap).
{
  const m = new BF.Machine(fs.readFileSync(path.join(__dirname, "..", "islands", "counter.bf"), "utf8"));
  m.run();
  m.takeOutput();
  let bad = 0;
  for (let n = 1; n <= 256; n++) {
    m.feed(2);
    m.run();
    if (dec(m.takeOutput()) !== counterHtml(n % 256)) bad++;
  }
  check("counter full range via plus (bad count)", bad, 0);
}

// Toggle: start, toggle x2.
const BTN = '<button data-ev="1">Toggle</button>';
const PARA = '<p>Hello from Brainfuck!</p>';
const toggleHtml = (visible) => BTN + (visible ? PARA : "");
runSequence(
  path.join(__dirname, "..", "islands", "toggle.bf"),
  { list: [{ byte: 1, state: 1 }, { byte: 1, state: 0 }].map((e) => ({ byte: e.byte, state: e.state })) },
  (s) => toggleHtml(s === 1),
  "toggle"
);

console.log("island tests: " + (failures ? failures + " failed" : "all passed"));
process.exit(failures ? 1 : 0);
