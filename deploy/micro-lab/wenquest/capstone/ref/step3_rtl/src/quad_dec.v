// 贯通项目步骤三参考解：正交编码器解码与 16 位计数。
// 1. 同步：A、B 来自芯片外部，与时钟无关，各用两级触发器同步，防止亚稳态。
// 2. 去抖：同步后的电平要连续 FILTER 个时钟不变才被采用，滤掉电机线上的短毛刺。
// 3. 四倍频解码：A、B 每变一次（一个格雷码步）计数加一或减一；A 超前 B 为正转。
//    同时变化（跳过一步）是非法的，计入 err 但不计数。
// 4. 计数为 16 位有符号数，溢出时回绕；dir 为最近一步的方向（1 = 正转）。
// 5. 复位后第一次被采用的状态只作为起点（编码器停在哪一格都可以），不计数、不报错。
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
    // two-flop synchronisers
    reg [1:0] a_s, b_s;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            a_s <= 2'b00;
            b_s <= 2'b00;
        end else begin
            a_s <= {a_s[0], a_in};
            b_s <= {b_s[0], b_in};
        end
    end

    // glitch filter: accept a new (A, B) level only after FILTER stable clocks
    localparam FW = $clog2(FILTER + 1);
    reg [1:0]    cand, stable;
    reg [FW-1:0] same;
    reg          valid;                // stable holds a real, accepted state
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cand   <= 2'b00;
            stable <= 2'b00;
            same   <= 0;
            valid  <= 1'b0;
        end else if ({a_s[1], b_s[1]} != cand) begin
            cand <= {a_s[1], b_s[1]};
            same <= 0;
        end else if (same < FILTER) begin
            same <= same + 1'b1;
        end else begin
            stable <= cand;
            valid  <= 1'b1;
        end
    end

    // x4 decoding: compare the accepted state with the previous one
    reg [1:0] prev;
    reg       primed;                  // prev holds the first accepted state: decoding may start
    wire [3:0] step = {prev, stable};
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prev   <= 2'b00;
            primed <= 1'b0;
            count  <= 16'd0;
            dir    <= 1'b1;
            err    <= 1'b0;
        end else if (!primed) begin
            if (valid) begin           // the first accepted state is only the starting point
                prev   <= stable;
                primed <= 1'b1;
            end
        end else begin
            prev <= stable;
            case (step)
                // forward (A leads B): 00 → 10 → 11 → 01 → 00
                4'b0010, 4'b1011, 4'b1101, 4'b0100: begin count <= count + 16'd1; dir <= 1'b1; end
                // reverse: 00 → 01 → 11 → 10 → 00
                4'b0001, 4'b0111, 4'b1110, 4'b1000: begin count <= count - 16'd1; dir <= 1'b0; end
                // both lines changed at once: a step was missed
                4'b0011, 4'b1100, 4'b0110, 4'b1001: err <= 1'b1;
                default: ;
            endcase
        end
    end
endmodule
`default_nettype wire
