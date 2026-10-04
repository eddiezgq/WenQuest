"""贯通项目步骤三起始文件：用 cocotb 验证电机控制芯片。test_pwm_duty 是写好的示范，其余测试由你完成。

六个测试：
  test_pwm_duty        占空比 0、64、128、200、255 时，一个 PWM 周期里高电平的时钟数 = 4 × duty
  test_brake           刹车一拉高，PWM 在同一个时钟内变低
  test_encoder_steps   正转 40 步、反转 25 步，计数 = 15；转向输出跟着变
  test_glitch          A 相上 2 个时钟宽的毛刺不计数
  test_wrap            计数从 0 再减 1 变成 0xFFFF（16 位回绕，作为有符号数即 −1）
  test_motor           闭环检验：芯片的 PWM 驱动一个直流电机模型，电机转动产生编码器 A、B 信号送回芯片，
                       芯片的计数必须和电机实际转过的角度一致（误差不超过 2 个计数），正反转都要对

电机模型（一阶）：平均电压 V = duty/256 · Vbus · (dir ? +1 : −1)，
  稳态转速 ω∞ = Kv · V，dω/dt = (ω∞ − ω)/τ；编码器 1000 线，四倍频后每转 4000 个计数。
  为了让仿真几毫秒就能看到加速、稳定、反转，机械时间常数 τ 取 0.5 ms（真实小电机约 20 ms），
  这只缩短时间，不影响要检验的逻辑；电机最高转速 50 转/秒（3000 转/分）。
"""
import math

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, Timer

CLK_NS = 50                     # 20 MHz
PERIOD = 4 * 256                # clocks per PWM period
GRAY = [0b00, 0b10, 0b11, 0b01]  # (A, B) in forward order: A leads B


def clock(dut):
    try:
        return Clock(dut.clk, CLK_NS, unit="ns")       # cocotb 2.x
    except TypeError:
        return Clock(dut.clk, CLK_NS, units="ns")      # cocotb 1.x


async def ns(t):
    """等待 t 纳秒（cocotb 2.x 写 unit=，1.x 写 units=，这里两种都处理）。"""
    try:
        await Timer(t, unit="ns")
    except TypeError:
        await Timer(t, units="ns")


class Pins:
    """The bidirectional inputs: A, B, dir, brake, sel on uio_in[4:0]."""
    def __init__(self, dut):
        self.dut, self.a, self.b, self.dir, self.brake, self.sel = dut, 0, 0, 1, 0, 0

    def put(self):
        self.dut.uio_in.value = self.a | self.b << 1 | self.dir << 2 | self.brake << 3 | self.sel << 4


async def reset(dut):
    cocotb.start_soon(clock(dut).start())
    p = Pins(dut)
    dut.ena.value = 1
    dut.ui_in.value = 0
    p.put()
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    return p


def pwm(dut):
    return (int(dut.uio_out.value) >> 5) & 1


async def read_count(dut, p) -> int:
    vals = []
    for s in (0, 1):
        p.sel = s; p.put()
        await ClockCycles(dut.clk, 4)                 # sel passes a two-flop synchroniser
        vals.append(int(dut.uo_out.value))
    p.sel = 0; p.put()
    return vals[0] | vals[1] << 8


def signed16(x):
    return x - 0x10000 if x & 0x8000 else x


async def step(dut, p, pos, n, gap=20):
    """Move the encoder n steps (negative = reverse) from position pos, gap clocks between steps."""
    for _ in range(abs(n)):
        pos += 1 if n > 0 else -1
        p.a, p.b = GRAY[pos % 4] >> 1, GRAY[pos % 4] & 1
        p.put()
        await ClockCycles(dut.clk, gap)
    return pos


@cocotb.test()
async def test_pwm_duty(dut):
    p = await reset(dut)
    for duty in (0, 64, 128, 200, 255):
        dut.ui_in.value = duty
        await ClockCycles(dut.clk, 2 * PERIOD)          # the new duty is taken at the start of a period
        high = 0
        for _ in range(PERIOD):
            await RisingEdge(dut.clk)
            high += pwm(dut)
        assert abs(high - 4 * duty) <= 4, f"duty {duty}: {high} high clocks in a period, expected {4 * duty}"
        dut._log.info("duty %d → %d/%d high clocks (%.1f %%)", duty, high, PERIOD, 100 * high / PERIOD)


@cocotb.test()
async def test_brake(dut):
    """刹车一拉高，PWM 在同一个时钟内变低；松开后恢复。提示：改 brake 后 await ns(1) 再读 pwm(dut)，不要等时钟沿。"""
    p = await reset(dut)
    # ===== 在这里完成 =====
    raise NotImplementedError("test_brake")


@cocotb.test()
async def test_encoder_steps(dut):
    """正转 40 步、反转 25 步，计数应为 15；转向输出（uio_out[7]）跟着变。提示：用上面的 step() 和 read_count()。"""
    p = await reset(dut)
    # ===== 在这里完成 =====
    raise NotImplementedError("test_encoder_steps")


@cocotb.test()
async def test_glitch(dut):
    """A 相（以及 B 相）上 2 个时钟宽的毛刺不应计数。注意：被计入的毛刺会先加一再减一，只看最后的计数发现不了，
    要在毛刺之后的每个时钟检查 uo_out（sel = 0 时为计数低字节）都不变。"""
    p = await reset(dut)
    # ===== 在这里完成 =====
    raise NotImplementedError("test_glitch")


@cocotb.test()
async def test_wrap(dut):
    """从 0 反转一步，计数应为 0xFFFF（16 位回绕）。"""
    p = await reset(dut)
    # ===== 在这里完成 =====
    raise NotImplementedError("test_wrap")


class Motor:
    """直流电机 + 1000 线编码器模型（一阶）。每个时钟调用一次 tick(pwm, direction)，返回轴的位置（编码器计数）。
    平均电压按每个 PWM 周期测得的占空比更新；转速 w 的单位是转/秒（rev/s），θ 以编码器计数为单位（每转 4000 个）。
    读芯片计数（read_count 要拨 sel、等几个时钟）时可以暂停调用 tick，模型随之暂停，不影响比较。"""
    TAU, KV, VBUS, LINES = 0.5e-3, 50.0 / 12.0, 12.0, 1000

    def __init__(self):
        self.w, self.theta, self.high, self.v, self.k = 0.0, 0.0, 0, 0.0, 0

    def tick(self, pwm_level, direction):
        dt = CLK_NS * 1e-9
        self.high += pwm_level
        self.k += 1
        if self.k % PERIOD == 0:
            self.v = self.high / PERIOD * self.VBUS * (1 if direction else -1)
            self.high = 0
        self.w += (self.KV * self.v - self.w) / self.TAU * dt
        self.theta += self.w * 4 * self.LINES * dt
        return math.floor(self.theta)          # the shaft position in encoder counts


@cocotb.test()
async def test_motor(dut):
    """闭环检验：芯片的 PWM 驱动 Motor 模型，模型转过的位置变成 A、B 信号送回芯片（每个时钟最多走一步，
    用 GRAY 表），先正转 3 ms（duty 180），再反转 4 ms（duty 120）；每段结束时芯片计数与模型位置之差 ≤ 2，
    反转段结束时电机确实在反转、转向输出为 0。"""
    p = await reset(dut)
    m = Motor()
    # ===== 在这里完成 =====
    raise NotImplementedError("test_motor")
