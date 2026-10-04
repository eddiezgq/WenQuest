// 第 17 轮附 4c：8 位计数器，RTL→GDS 验收用（LibreLane + SKY130 sky130_fd_sc_hd）
module counter8 (
    input  wire       clk,
    input  wire       rst,
    input  wire       en,
    output reg  [7:0] q
);
    always @(posedge clk)
        if (rst)     q <= 8'd0;
        else if (en) q <= q + 8'd1;
endmodule
