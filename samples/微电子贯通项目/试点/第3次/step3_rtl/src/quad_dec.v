// 贯通项目步骤三：正交编码器解码与 16 位计数（起始文件）。端口和参数不要改。
// 要求（详见步骤三指导书）：
//   1. A、B 是芯片外部来的异步信号：各用两级触发器同步；
//   2. 去抖：同步后的 (A, B) 变化后连续保持 FILTER 个时钟以上不变才被采用，短毛刺不计数；
//   3. 四倍频：A、B 每变化一次计数加一或减一；正转时序 (A,B) = 00 → 10 → 11 → 01 → 00（A 超前 B）；
//      A、B 同时变化（跳步）不计数，并把 err 置 1；
//   4. count 为 16 位，溢出回绕；dir 为最近一步的方向（1 = 正转），复位后为 1；
//   5. rst_n 为低时清零；复位后第一次被采用的状态只作为起点（编码器可能停在任意一格），不计数、不报错。
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
    // 1. two-flop synchronisers for A and B
    reg [1:0] s1, s2;                       // {A, B}
    // 2. debounce: cand = last synchronised value, stab = clocks it has stayed unchanged
    localparam SW = $clog2(FILTER + 2) + 1;
    reg [1:0]    cand;
    reg [SW-1:0] stab;
    // 3. accepted state
    reg [1:0] state;
    reg       valid;                        // 0 until the first accepted state after reset

    // next state in the forward order 00 -> 10 -> 11 -> 01 -> 00
    function [1:0] fwd(input [1:0] s);
        case (s)
            2'b00: fwd = 2'b10;
            2'b10: fwd = 2'b11;
            2'b11: fwd = 2'b01;
            default: fwd = 2'b00;
        endcase
    endfunction

    // accepted when unchanged for more than FILTER clocks (stab counts the clocks after the change)
    wire accept = (s2 == cand) && (stab == FILTER);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s1 <= 2'b00; s2 <= 2'b00;
            cand <= 2'b00; stab <= {SW{1'b0}};
            state <= 2'b00; valid <= 1'b0;
            count <= 16'd0; dir <= 1'b1; err <= 1'b0;
        end else begin
            s1 <= {a_in, b_in};
            s2 <= s1;
            if (s2 != cand) begin
                cand <= s2;
                stab <= {SW{1'b0}};
            end else if (stab <= FILTER) begin
                stab <= stab + 1'b1;
            end
            if (accept) begin
                if (!valid) begin
                    valid <= 1'b1;               // first accepted state: starting point only
                    state <= cand;
                end else if (cand != state) begin
                    state <= cand;
                    if (cand == fwd(state)) begin
                        count <= count + 16'd1; dir <= 1'b1;
                    end else if (state == fwd(cand)) begin
                        count <= count - 16'd1; dir <= 1'b0;
                    end else begin
                        err <= 1'b1;             // both lines changed: missed step, held until reset
                    end
                end
            end
        end
    end

endmodule
`default_nettype wire
