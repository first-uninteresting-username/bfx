# bfx render design notes (working notes, not user docs)

Memory layout (cells in the table region are 15 lanes per element, first element at cell 75):
- Cells 0..47: flags and scratch (see gen_main.py for the exact map).
- Cells 48..63: name register (16 cells, pad value 1).
- Cell 64: IO cell (`,` reads here, `.` writes here, HOME query lane).
- Cells 65..71, 73: scratch that is zero between blocks. 72 must stay zero (HOME marker). 74: sweep status.
- Element base b: 0 data, 1..3 work, 4 query carry, 5..7 work, 8 cursor, 9 staging,
  10 not cursor, 11 name first flag, 12 in table marker, 13 layout cursor store, 14 status carry.

Sweeps (each starts and ends on cell 64, each walks element to element with the marker lane):
- loader: components bytes -> elements (stops at zero byte).
- reset: cursor := name first flag.
- pass: one name byte; cursor advances where data equals the byte.
- emit normal: writes the cursor byte, pauses (status 1) on dollar, ends (status 2) before newline at sign sign.
- emit skip: advances without output; status 4 on advance, 6 when the body is empty.
- save/restore: cursor lane <-> store lane (for the layout body while components run).

Known limits to document: names longer than 16 bytes keep only the last 16; names end at
open paren, space, newline, at sign or end of input; duplicate names are not checked.
