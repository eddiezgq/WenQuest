(* 程序 2.3.2  星三角启动控制电路（图 2.3.4）写成逻辑式 *)
PROGRAM Main
  VAR
    KT1 : TON;      (* 时间继电器 KT1：星形运行 5 s 后切换到三角形 *)
  END_VAR

  (* 主接触器 KM1：按 S1 启动并自锁，停止按钮 S2、热继电器 F1 断开它 *)
  KM1_Main := (S1_Start OR KM1_Aux) AND S2_Stop AND F1_OL;

  (* KT1 从启动开始计时，切到三角形以后（KM3 吸合）退出 *)
  KT1(IN := KM1_Main AND NOT KM3_Aux, PT := T#5s);

  (* 星形 KM2：启动后先吸合，KT1 到时断开；KM3 的常闭辅助触点互锁 *)
  KM2_Star := KM1_Main AND NOT KT1.Q AND NOT KM3_Aux;

  (* 三角形 KM3：KT1 到时、并且 KM2 已经释放（KM2 的常闭辅助触点）才吸合，然后自锁 *)
  KM3_Delta := KM1_Main AND (KT1.Q OR KM3_Aux) AND NOT KM2_Aux;
END_PROGRAM
