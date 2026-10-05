(* 程序 4.3.1  计件，外加一段“别的工作”：FOR 循环执行 n 次，用来模拟程序变长（数据记录、通信处理……） *)
PROGRAM Main
  VAR
    cnt : CTU;            (* 工件计数 *)
    n : DINT := 1000;     (* “别的工作”的循环次数：改它，看扫描时间怎样变 *)
    i : DINT;
    work : DINT;
  END_VAR
  cnt(CU := B1_Part, R := S1_Reset, PV := 30000);
  FOR i := 1 TO n DO
    work := work + 1;
  END_FOR;
  H1_Count := B1_Part;
END_PROGRAM
