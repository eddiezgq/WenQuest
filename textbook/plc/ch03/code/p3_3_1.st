(* 程序 3.3.1  数按钮按下的次数：计数器 cnt 对输入 S1_Count 的上升沿计数，S2_Reset 清零 *)
PROGRAM Main
  VAR
    cnt : CTU;
  END_VAR
  cnt(CU := S1_Count, R := S2_Reset, PV := 1000);
  H1_Done := cnt.Q;
END_PROGRAM
