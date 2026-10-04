// 贯通项目步骤三：正交编码器解码与 16 位计数（起始文件）。端口和参数不要改。
// 要求（详见步骤三指导书）：
//   1. A、B 是芯片外部来的异步信号：各用两级触发器同步；
//   2. 去抖：同步后的 (A, B) 连续 FILTER 个时钟不变才被采用，短毛刺不计数；
//   3. 四倍频：A、B 每变化一次计数加一或减一；正转时序 (A,B) = 00 → 10 → 11 → 01 → 00（A 超前 B）；
//      A、B 同时变化（跳步）不计数，并把 err 置 1；
//   4. count 为 16 位，溢出回绕；dir 为最近一步的方向（1 = 正转），复位后为 1；
//   5. rst_n 为低时清零。
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
    // 1. two-flop synchronisers
    reg [1:0] a_s, b_s;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            a_s <= 2'b00; b_s <= 2'b00;
        end else begin
            a_s <= {a_s[0], a_in};
            b_s <= {b_s[0], b_in};
        end
    end
    wire [1:0] ab = {a_s[1], b_s[1]};

    // 2. debounce: (A,B) must stay the same for FILTER clocks before it is accepted
    localparam FW = $clog2(FILTER + 1);
    reg [1:0]    cand, stable;
    reg [FW-1:0] fcnt;

    // 3. x4 decoding: Gray (A,B) 00->0, 10->1, 11->2, 01->3 in forward order, i.e. index = {B, A^B}
    wire [1:0] pos_old = {stable[0], stable[1] ^ stable[0]};
    wire [1:0] pos_new = {cand[0],   cand[1] ^ cand[0]};
    wire [1:0] delta   = pos_new - pos_old;     // 1 = forward, 3 = reverse, 2 = missed step
    wire       accept  = (ab == cand) && (fcnt >= FILTER - 1) && (cand != stable);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cand   <= 2'b00;
            stable <= 2'b00;
            fcnt   <= 0;
            count  <= 16'd0;
            dir    <= 1'b1;
            err    <= 1'b0;
        end else begin
            if (ab != cand) begin
                cand <= ab;                     // level changed: restart the filter (this is sample 1)
                fcnt <= 1;
            end else if (fcnt < FILTER) begin
                fcnt <= fcnt + 1'b1;
            end
            if (accept) begin                   // FILTER equal samples in a row: take the new state
                stable <= cand;
                case (delta)
                    2'd1: begin count <= count + 16'd1; dir <= 1'b1; end
                    2'd3: begin count <= count - 16'd1; dir <= 1'b0; end
                    default: err <= 1'b1;       // both lines changed at once: not counted
                endcase
            end
        end
    end

endmodule
`default_nettype wire
