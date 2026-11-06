Counter island with minus and plus buttons and a decimal count from zero to 255
Cells zero N one EV two H three T four O five flag six W seven Y eight Z nine P ten RUN
>>>>>>>>>>+
  cell 10 RUN flag set to 1 and pointer on it
[
  main loop start
<<<<<<<<[-]>[-]>[-]
  clear H T O at cells 2 3 4 pointer ends on O
<<<<[->>>>>>+>+<<<<<<<]
  copy N to W cell 6 and Y cell 7 pointer on N
>>>>>>>[-<<<<<<<+>>>>>>>]
  restore N from cell 7 pointer on cell 7
<
  pointer to W cell 6
[
  extraction loop while W nonzero
-
  W decrement
<<+
  O increment pointer on O
[->>>+>+<<<<]
  copy O to cells 7 and 8 pointer on O
>>>>[-<<<<+>>>>]
  restore O from cell 8 pointer on cell 8
<----------
  cell 7 becomes O minus 10 pointer on cell 7
<<+
  flag F cell 5 set to 1
>>[[-]<<[-]>>]
  flag F cleared unless O equals 10
<<
  pointer on flag cell 5
[
  if O equals 10
-
  clear flag
<[-]
  O becomes 0
<+
  T increment pointer on T
[->>>>+>+<<<<<]
  copy T to cells 7 and 8 pointer on T
>>>>>[-<<<<<+>>>>>]
  restore T pointer on cell 8
<----------
  cell 7 becomes T minus 10
<<+
  flag F set to 1
>>[[-]<<[-]>>]
  flag cleared unless T equals 10
<<
  pointer on flag cell 5
[
  if T equals 10
-
  clear flag
<<[-]
  T becomes 0
<+
  H increment
>>>
  pointer on flag cell 5
]
  end if T equals 10
]
  end if O equals 10
>
  pointer to W cell 6
]
  end extraction loop
>>>
  pointer to print cell 9
++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ . ++++++++++ ++++++++++ ++++++++++ ++++++++. ++++++++++ +++++++++. -. . -----. -. ---------- ---------- ---------- ---------- ---------- ---------- ---------- --------. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++. ---. ++++++++++ +++++++++. ---------- ---------. ---------- ---------- ---------- ---------- ---------- --. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++. ++++++++++ +++++++. ---------- ---------- ---------- ---------- ---------- -------. ---------- ---------- -------. ++++++++++ +++++. ---------- -----. ++++++++++ ++++++++++ ++++++++. ---------- -------. ++++++++++ +++++. ---------- ---. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ +. ++++++++++ +++++++++. -. . -----. -. ---------- ---------- ---------- ---------- --------. ---------- ---------- ---------- . ++++++++++ ++++++++++ ++++++++. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ +++++. ---. ---------- -----. ++++++++++ +++. ---------- ---------- ---------- ---------- --------.
  print first constant text
[-]
  clear print cell
<<<<<<<
  pointer to H cell 2
[
  if H nonzero
>>>+<<<
  flag SZ cell 5 set to 1
>>>>>>
  pointer to cell 8
++++++++[>++++++<-]>
  print cell 9 becomes 48
<<<<<<<
  pointer to H
[->>>>>>>+<<<<<<<]
  move H into print cell
>>>>>>>.
  print digit of H
[-]
  clear print cell
<<<<<<<
  pointer to H
]
  end if H nonzero
>>>
  pointer to SZ cell 5
[
  if SZ set print T even when zero
-
  clear SZ
<<
  pointer to T cell 3
>>>>>
  pointer to cell 8
++++++++[>++++++<-]>
  print cell 9 becomes 48
<<<<<<
  pointer to T
[->>>>>>+<<<<<<]
  move T into print cell
>>>>>>.
  print digit of T
[-]
  clear print cell
<<<<<<
  pointer to T
>>
  pointer to SZ cell 5
]
  end if SZ
<<
  pointer to T cell 3
[
  if T nonzero
>>>>>
  pointer to cell 8
++++++++[>++++++<-]>
  print cell 9 becomes 48
<<<<<<
  pointer to T
[->>>>>>+<<<<<<]
  move T into print cell
>>>>>>.
  print digit of T
[-]
  clear print cell
<<<<<<
  pointer to T
]
  end if T nonzero
>
  pointer to O cell 4
>>>>
  pointer to cell 8
++++++++[>++++++<-]>
  print cell 9 becomes 48
<<<<<
  pointer to O
[->>>>>+<<<<<]
  move O into print cell
>>>>>.
  print digit of O
[-]
  clear print cell
++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ . ---------- ---. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++. ---. ---------- -----. ++++++++++ +++. ---------- ---------- ---------- ---------- --------. ---------- ---------- ---------- . ++++++++++ ++++++++++ ++++++++. ++++++++++ ++++++++++ ++++++++++ ++++++++. ++++++++++ +++++++++. -. . -----. -. ---------- ---------- ---------- ---------- ---------- ---------- ---------- --------. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++. ---. ++++++++++ +++++++++. ---------- ---------. ---------- ---------- ---------- ---------- ---------- --. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++. ++++++++++ +++++++. ---------- ---------- ---------- ---------- ---------- -------. ---------- ---------- -------. ++++++++++ ++++++. ---------- ------. ++++++++++ ++++++++++ ++++++++. ---------- ---------. ++++++++++ +++++++. ---------- ---. ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ +. ++++++++++ +++++++++. -. . -----. -. ---------- ---------- ---------- ---------- --------.
  print second constant text
[-]
  clear print cell
<<<<<<<<
  pointer to EV cell 1
,
  wait for event byte into EV
[->>>>>>+>+<<<<<<<]
  move EV into cells 7 and 8 pointer on EV
>>>>>>-
  cell 7 becomes EV minus 1
<<+
  flag F set to 1
>>[[-]<<[-]>>]
  flag cleared unless EV equals 1
<<
  pointer on flag
[-<<<<<->>>>>]
  if EV equals 1 decrement N
>>>--
  cell 8 becomes EV minus 2
<<<+
  flag F set to 1
>>>[[-]<<<[-]>>>]
  flag cleared unless EV equals 2
<<<
  pointer on flag
[-<<<<<+>>>>>]
  if EV equals 2 increment N
>>>>>
  pointer to cell 10
]
  main loop end
