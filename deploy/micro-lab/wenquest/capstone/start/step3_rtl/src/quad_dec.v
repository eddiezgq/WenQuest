// 贯通项目步骤三：正交编码器解码与 16 位计数（起始文件）。端口和参数不要改。
// 要求（详见步骤三指导书）：
//   1. A、B 是芯片外部来的异步信号：各用两级触发器同步；
//   2. 去抖：同步后的 (A, B) 变化后要连续保持超过 FILTER 个时钟不变才被采用（恰好 FILTER 个时钟宽的脉冲不采用）；
//   3. 四倍频：A、B 每变化一次计数加一或减一；正转时序 (A,B) = 00 → 10 → 11 → 01 → 00（A 超前 B）；
//      A、B 同时变化（跳步）不计数、不改方向，新状态作为当前位置，err 置 1 并保持到复位；
//   4. count 为 16 位，溢出回绕；dir 为最近一步的方向（1 = 正转），复位后为 1；
//   5. rst_n 为低时清零（异步复位）；复位后第一次被采用的状态只作为起点（编码器可能停在任意一格），不计数、不报错。
`default_nettype none
module quad_dec #(
    parameter FILTER = 4
) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        a_in,
    input  wire        b_in,
    output reg  [15:0] count,
    output reg         dir,
    output reg         err
);
    // ===== 在这里完成 =====

endmodule
`default_nettype wire
