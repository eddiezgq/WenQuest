(* 程序 4.7.1  计件：普通输入 + 计数器（原程序）与读高速计数器（改后）并排 *)
PROGRAM Main
  VAR
    cnt : CTU;                 (* 原程序：对 B1_Part 的上升沿计数，每次扫描看一次 *)
    base : DINT;               (* 改后：清零时记下高速计数器的读数 *)
    countHsc : DINT;          (* 改后：本班的件数 *)
    n : DINT := 5000;          (* 其余程序，用一个循环代替，使扫描时间约 10 ms *)
    i : DINT;
    work : DINT;
  END_VAR
  cnt(CU := B1_Part, R := S1_Reset, PV := 30000);

  IF S1_Reset THEN
    base := HSC1_CV;
  END_IF;
  countHsc := HSC1_CV - base;

  FOR i := 1 TO n DO
    work := work + 1;
  END_FOR;
  H1_Count := B1_Part;
END_PROGRAM
