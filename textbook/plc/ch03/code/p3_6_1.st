(* 程序 3.6.1  用普通输入数脉冲：计数器 cnt 对 B1_Pulse 的上升沿计数 *)
PROGRAM Main
  VAR
    cnt : CTU;
  END_VAR
  cnt(CU := B1_Pulse, R := S2_Reset, PV := 30000);
END_PROGRAM
