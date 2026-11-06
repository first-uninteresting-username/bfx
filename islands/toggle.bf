Toggle island with a button that shows and hides a paragraph
Cells zero V one EV two copy three flag four copy five P six new seven RUN
>>>>>>>+
  cell seven RUN flag set to one and pointer on it
[
  main loop start
<<
  pointer to print cell five
++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ . ++++++++++ ++++++++++ ++++++++++ ++++++++. ++++++++++ +++++++++. -. . -----. -. ---------- ---------- ---------- ---------- ---------- ---------- ---------- --------. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++. ---. ++++++++++ +++++++++. ---------- ---------. ---------- ---------- ---------- ---------- ---------- --. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++. ++++++++++ +++++++. ---------- ---------- ---------- ---------- ---------- -------. ---------- ---------- -------. ++++++++++ +++++. ---------- -----. ++++++++++ ++++++++++ ++++++++. ++++++++++ ++++++++++ ++. ++++++++++ ++++++++++ +++++++. --------. . +++++. -------. ---------- ---------- ---------- ---------- -. ---------- ---. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ +. ++++++++++ +++++++++. -. . -----. -. ---------- ---------- ---------- ---------- --------.
  print the button
[-]
  clear print cell
<<<<<
  pointer to visible flag cell zero
[->>>>+>+<<<<<]
  copy visible flag to cells four and five pointer on zero
>>>>>[-<<<<<+>>>>>]
  restore visible flag from cell five pointer on five
<
  pointer to copy cell four
[
  if visible print the paragraph
-
  clear copy
>
  pointer to print cell five
++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ . ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++. ---------- ---------- ---------- ---------- ---------- . ++++++++++ . ++++++++++ ++++++++++ +++++++++. +++++++. . +++. ---------- ---------- ---------- ---------- ---------- ---------- ---------- ---------. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ . ++++++++++ ++. ---. --. ---------- ---------- ---------- ---------- ---------- ---------- ---------- -------. ++++++++++ ++++++++++ ++++++++++ ++++. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++. ---------- -------. ++++++++. +++++. --------. ++++++++++ +++++. ---------- --------. ++++++++. ---------- ---------- ---------- ---------- ---------- ---------- ---------- ----. ++++++++++ ++++++++++ +++++++. ---------- ---. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ +++++. ---------- ---------- ---------- ---------- ---------- .
  print the paragraph
[-]
  clear print cell
<
  pointer to copy cell four
]
  end if visible
<<<
  pointer to event cell one
,
  wait for event byte into event cell
[->+<]
  move event into cell two pointer on event cell
>-
  cell two becomes event minus one
>+
  flag cell three set to one
<[[-]>[-]<]
  flag cleared unless event equals one pointer on cell two
>
  pointer on flag cell three
[
  if event equals one flip visible
-
  clear flag
<<<
  pointer to visible cell zero
>>>>>>+<<<<<<
  new value cell six set to one
[[-]>>>>>>[-]<<<<<<]
  if visible was nonzero clear visible and new value
>>>>>>[-<<<<<<+>>>>>>]
  visible becomes new value pointer on cell six
<<<
  pointer to flag cell three
]
  end if event equals one
>>>>
  pointer to RUN cell seven
]
  main loop end
