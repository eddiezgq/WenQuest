// 贯通项目：机器人关节电机控制芯片的数字部分（PWM 发生器 + 正交编码器计数器）。
// 顶层按 Tiny Tapeout 的用户模块格式：8 个输入 ui_in、8 个输出 uo_out、8 个双向口 uio、时钟、复位（低有效）、使能。
//
// 引脚分配
//   ui_in[7:0]   占空比 duty（0–255，对应 0–255/256）
//   uio[0] 输入  编码器 A 相
//   uio[1] 输入  编码器 B 相
//   uio[2] 输入  方向命令 dir_cmd（1 = 正转）
//   uio[3] 输入  刹车 brake（1 = PWM 立即关断）
//   uio[4] 输入  读数选择 sel（0 = 计数低字节，1 = 高字节）
//   uio[5] 输出  PWM（接 H 桥驱动芯片的使能端）
//   uio[6] 输出  方向输出（接 H 桥的方向端；刹车时保持）
//   uio[7] 输出  编码器测得的转向（1 = 正转）
//   uo_out[7:0]  计数值的低字节或高字节（由 sel 选择）
`default_nettype none
module tt_um_wenquest_motor (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);
    wire        pwm;
    wire [15:0] count;
    wire        enc_dir, enc_err;

    // the control inputs are slow buttons or MCU pins: synchronise them too
    reg [1:0] dir_s, brake_s, sel_s;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            dir_s   <= 2'b11;
            brake_s <= 2'b11;          // brake on while coming out of reset
            sel_s   <= 2'b00;
        end else begin
            dir_s   <= {dir_s[0], uio_in[2]};
            brake_s <= {brake_s[0], uio_in[3]};
            sel_s   <= {sel_s[0], uio_in[4]};
        end
    end

    pwm_gen #(.PRESCALE(4)) u_pwm (
        .clk(clk), .rst_n(rst_n), .duty(ui_in), .brake(brake_s[1] | uio_in[3]), .pwm(pwm)
    );

    quad_dec #(.FILTER(4)) u_dec (
        .clk(clk), .rst_n(rst_n), .a_in(uio_in[0]), .b_in(uio_in[1]),
        .count(count), .dir(enc_dir), .err(enc_err)
    );

    assign uo_out  = sel_s[1] ? count[15:8] : count[7:0];
    assign uio_out = {enc_dir, dir_s[1], pwm, 5'b00000};
    assign uio_oe  = 8'b1110_0000;

    wire _unused = &{ena, uio_in[7:5], enc_err, 1'b0};
endmodule
`default_nettype wire
