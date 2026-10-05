(* 程序 4.6.1  扫描带来的三件“怪事”：一拍延迟、双线圈、程序顺序决定结果 *)
PROGRAM Main
  (* 1. 一拍延迟：H2 用的是 H1 上一次扫描的值 *)
  H2_Late := H1_Copy;
  H1_Copy := S1_In;

  (* 2. 双线圈：Y1 被写了两次，只有后一次起作用 *)
  Y1_Out := S1_In;
  Y1_Out := S2_In;

  (* 3. 顺序：先算 H3_First，再用它，就没有延迟 *)
  H3_First := S1_In;
  H4_Same := H3_First;
END_PROGRAM
