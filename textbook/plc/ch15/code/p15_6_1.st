(* 程序 15.6.1  三层电梯：用 CASE 写的状态机（呼梯登记、关门、运行、平层、开门） *)
TYPE E_Lift : (DOOR_OPEN, CLOSING, MOVING); END_TYPE

PROGRAM Main
  VAR
    state : E_Lift := DOOR_OPEN;
    call : ARRAY[1..3] OF BOOL;   (* 已登记的呼梯 *)
    floor : INT := 1;             (* 最近经过的楼层 *)
    target : INT;                 (* 要去的楼层，0 表示没有 *)
    tClose : TON;                 (* 关门时限：门被挡住就重新开门 *)
    atTarget : BOOL;
  END_VAR

  (* 登记呼梯；记住最近经过的楼层 *)
  IF S_C1 THEN call[1] := TRUE; END_IF;
  IF S_C2 THEN call[2] := TRUE; END_IF;
  IF S_C3 THEN call[3] := TRUE; END_IF;
  IF B_F1 THEN floor := 1; ELSIF B_F2 THEN floor := 2; ELSIF B_F3 THEN floor := 3; END_IF;
  atTarget := (target = 1 AND B_F1) OR (target = 2 AND B_F2) OR (target = 3 AND B_F3);

  CASE state OF
    DOOR_OPEN:                                   (* 停在某层、门开着 *)
      IF B_F1 OR B_F2 OR B_F3 THEN call[floor] := FALSE; END_IF;   (* 本层的呼梯随到随消 *)
      target := 0;
      IF call[1] THEN target := 1; ELSIF call[2] THEN target := 2; ELSIF call[3] THEN target := 3; END_IF;
      IF target <> 0 AND B_DoorOpen THEN state := CLOSING; END_IF;
    CLOSING:
      tClose(IN := TRUE, PT := T#4s);
      IF B_DoorClosed THEN tClose(IN := FALSE); state := MOVING;
      ELSIF tClose.Q THEN tClose(IN := FALSE); state := DOOR_OPEN; END_IF;
    MOVING:
      IF atTarget THEN call[target] := FALSE; state := DOOR_OPEN; END_IF;
  END_CASE;

  K_Up    := state = MOVING AND target > floor AND NOT atTarget AND S_TopLim AND B_DoorClosed;
  K_Down  := state = MOVING AND target < floor AND NOT atTarget AND S_LowLim AND B_DoorClosed AND NOT K_Up;
  Y_DoorOpen  := state = DOOR_OPEN AND NOT B_DoorOpen;
  Y_DoorClose := state = CLOSING AND NOT B_DoorClosed;
  H_C1 := call[1]; H_C2 := call[2]; H_C3 := call[3];
END_PROGRAM
