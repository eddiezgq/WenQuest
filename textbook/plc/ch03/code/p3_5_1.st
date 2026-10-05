(* 程序 3.5.1  水箱液位：4–20 mA 液位计的标定、断线检测和加水阀的两位控制。
   模拟量输入 AI_Level：4 mA ↔ 0，20 mA ↔ 27648（低于 4 mA 为负数）；液位量程 0–2000 mm *)
PROGRAM Main
  VAR CONSTANT
    RAW_FS : REAL := 27648.0;     (* 20 mA 对应的数 *)
    LEVEL_FS : REAL := 2000.0;    (* 满量程液位，mm *)
    LOW : REAL := 800.0;          (* 低于它开阀加水，mm *)
    HIGH : REAL := 1500.0;        (* 高于它关阀，mm *)
  END_VAR
  VAR
    current : REAL;               (* 回路电流，mA *)
    level : REAL;                 (* 液位，mm *)
    wireBreak : BOOL;             (* 断线或变送器故障：电流低于 3.6 mA *)
    overRange : BOOL;             (* 超量程：电流高于 20.5 mA *)
  END_VAR

  current := 4.0 + 16.0 * INT_TO_REAL(AI_Level) / RAW_FS;
  level := LEVEL_FS * INT_TO_REAL(AI_Level) / RAW_FS;
  wireBreak := current < 3.6;
  overRange := current > 20.5;

  (* 两位控制：低于 LOW 开阀，高于 HIGH 关阀，中间保持；信号不可信时一律关阀 *)
  IF wireBreak OR overRange THEN
    Y1_Fill := FALSE;
  ELSIF level < LOW THEN
    Y1_Fill := TRUE;
  ELSIF level > HIGH THEN
    Y1_Fill := FALSE;
  END_IF;
  H3_LevelFault := wireBreak OR overRange;
END_PROGRAM
