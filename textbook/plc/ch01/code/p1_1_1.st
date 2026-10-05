(* 程序 1.1.1  上料输送线：启停、自锁、到末端停、卡料报警 *)
PROGRAM Main
  VAR
    tJam : TON;          (* 卡料监视：电机转了 20 s 料还没到末端 *)
    jammed : BOOL;       (* 卡料报警（记住，直到按启动复位） *)
  END_VAR

  (* 1. 卡料：电机一直在转、末端一直没料，20 s 后报警；按启动复位 *)
  tJam(IN := KM1_Run AND NOT B2_End, PT := T#20s);
  IF tJam.Q THEN jammed := TRUE; END_IF;
  IF S1_Start AND NOT KM1_Run THEN jammed := FALSE; END_IF;

  (* 2. 电机：按启动转（自锁），按停止、急停、过载、到末端或卡料就停 *)
  KM1_Run := (S1_Start OR KM1_Run) AND S2_Stop AND S0_EStop AND F1_Overload AND NOT B2_End AND NOT jammed;

  (* 3. 指示灯 *)
  H1_Run := KM1_Run;
  H2_Fault := jammed OR NOT F1_Overload;
END_PROGRAM
