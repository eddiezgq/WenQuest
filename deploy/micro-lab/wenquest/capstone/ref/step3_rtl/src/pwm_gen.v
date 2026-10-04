// 贯通项目步骤三参考解：8 位 PWM 发生器。
// 时钟 20 MHz，预分频 4 → 计数器每 200 ns 加一，256 级一周期 → 载波约 19.5 kHz（人耳听不到，常见电机驱动频率）。
// 占空比 duty/256：计数值 < duty 时输出高。duty 只在一个周期开始时装入，避免周期中途改变引起毛刺。
// brake 为高时输出立即为低（组合门控，不等周期结束）。
`default_nettype none
module pwm_gen #(
    parameter PRESCALE = 4
) (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] duty,
    input  wire       brake,
    output wire       pwm
);
    localparam PW = $clog2(PRESCALE);
    reg [PW-1:0] pre;
    reg [7:0]    cnt;
    reg [7:0]    duty_q;
    reg          pwm_q;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pre    <= 0;
            cnt    <= 8'd0;
            duty_q <= 8'd0;
            pwm_q  <= 1'b0;
        end else begin
            if (pre == PRESCALE - 1) begin
                pre <= 0;
                cnt <= cnt + 8'd1;
                if (cnt == 8'd255) duty_q <= duty;          // next period starts: take the new duty
            end else begin
                pre <= pre + 1'b1;
            end
            pwm_q <= (cnt < duty_q);
        end
    end

    assign pwm = pwm_q & ~brake;
endmodule
`default_nettype wire
