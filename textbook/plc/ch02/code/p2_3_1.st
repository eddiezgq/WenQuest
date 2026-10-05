(* 程序 2.3.1  电动机正反转控制电路（图 2.3.2）写成逻辑式：按钮互锁 + 接触器辅助触点互锁 *)
PROGRAM Main
  (* 正转：按 S1，或 KM1 已经吸合（自锁）；串入反转按钮 S3 的常闭触点（按钮互锁）、
     KM2 的常闭辅助触点（接触器互锁）、停止按钮 S2 和热继电器 F1 的常闭触点 *)
  KM1_Fwd := (S1_Fwd OR KM1_Aux) AND NOT S3_Rev AND NOT KM2_Aux AND S2_Stop AND F1_OL;

  (* 反转：与正转对称 *)
  KM2_Rev := (S3_Rev OR KM2_Aux) AND NOT S1_Fwd AND NOT KM1_Aux AND S2_Stop AND F1_OL;
END_PROGRAM
