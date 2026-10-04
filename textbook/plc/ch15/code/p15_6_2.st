(* 程序 15.6.2  三层电梯的顺序功能图写法：同一套 I/O、同样的测试 *)
PROGRAM Main
  VAR
    call : ARRAY[1..3] OF BOOL;
    floor : INT := 1;
    target : INT;
    atTarget : BOOL;
  END_VAR

  IF S_C1 THEN call[1] := TRUE; END_IF;
  IF S_C2 THEN call[2] := TRUE; END_IF;
  IF S_C3 THEN call[3] := TRUE; END_IF;
  IF B_F1 THEN floor := 1; ELSIF B_F2 THEN floor := 2; ELSIF B_F3 THEN floor := 3; END_IF;
  atTarget := (target = 1 AND B_F1) OR (target = 2 AND B_F2) OR (target = 3 AND B_F3);
  H_C1 := call[1]; H_C2 := call[2]; H_C3 := call[3];

  INITIAL_STEP Open: OpenDoor(N); Choose(N); END_STEP
  STEP Closing: Y_DoorClose(N); END_STEP
  STEP Moving: Drive(N); END_STEP
  STEP Arrive: Arrived(P); END_STEP

  ACTION OpenDoor:
    Y_DoorOpen := NOT B_DoorOpen;
  END_ACTION
  ACTION Choose:
    IF B_F1 OR B_F2 OR B_F3 THEN call[floor] := FALSE; END_IF;
    target := 0;
    IF call[1] THEN target := 1; ELSIF call[2] THEN target := 2; ELSIF call[3] THEN target := 3; END_IF;
  END_ACTION
  ACTION Drive:
    K_Up   := target > floor AND NOT atTarget AND S_TopLim AND B_DoorClosed;
    K_Down := target < floor AND NOT atTarget AND S_LowLim AND B_DoorClosed AND NOT K_Up;
  END_ACTION
  ACTION Arrived:
    K_Up := FALSE; K_Down := FALSE; call[target] := FALSE;
  END_ACTION

  TRANSITION FROM Open TO Closing := target <> 0 AND B_DoorOpen; END_TRANSITION
  TRANSITION FROM Closing TO Moving := B_DoorClosed; END_TRANSITION
  TRANSITION FROM Closing TO Open := Closing.T >= T#4s; END_TRANSITION       (* 门被挡住：重新开门 *)
  TRANSITION FROM Moving TO Arrive := atTarget; END_TRANSITION
  TRANSITION FROM Arrive TO Open := TRUE; END_TRANSITION
END_PROGRAM
