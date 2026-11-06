// Runs tests/interp_cases.json through runtime/bf.js (runToEnd).
"use strict";
const fs = require("fs");
const path = require("path");
const BF = require(path.join(__dirname, "..", "runtime", "bf.js"));

function fromHex(h) {
  const out = new Uint8Array(h.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(h.substr(i * 2, 2), 16);
  return out;
}
function toHex(bytes) {
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

const cases = JSON.parse(fs.readFileSync(path.join(__dirname, "interp_cases.json"), "utf8")).cases;
let failures = 0;
for (const c of cases) {
  let got;
  try {
    got = BF.runToEnd(c.program, fromHex(c.input_hex || ""), 10000000);
  } catch (e) {
    if (c.error_contains !== undefined && String(e.message).includes(c.error_contains)) continue;
    failures++;
    console.log("FAIL (js)", c.name, "unexpected error:", e.message);
    continue;
  }
  if (c.error_contains !== undefined) {
    failures++;
    console.log("FAIL (js)", c.name, "expected error, got output", toHex(got));
    continue;
  }
  if (toHex(got) !== c.output_hex) {
    failures++;
    console.log("FAIL (js)", c.name, "want", c.output_hex, "got", toHex(got));
  }
}
console.log("js interp: " + cases.length + " cases, " + failures + " failed");
process.exit(failures ? 1 : 0);
