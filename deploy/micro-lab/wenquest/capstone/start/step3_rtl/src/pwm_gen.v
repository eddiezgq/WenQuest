// 贯通项目步骤三：8 位 PWM 发生器（起始文件）。端口和参数不要改，顶层 project.v 按这个接口连接。
// 要求（详见步骤三指导书）：
//   1. 时钟 20 MHz，PRESCALE 分频后计数器加一，8 位计数器 0–255 循环，一个 PWM 周期 = PRESCALE × 256 个时钟；
//   2. 计数值 < 占空比时输出高；占空比只在每个周期开始时更新（避免周期中途跳变）；
//   3. brake 为高时 pwm 立即为低（不等时钟沿）；
//   4. rst_n 为低时所有寄存器清零。
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
    // ===== 在这里完成 =====

endmodule
`default_nettype wire
