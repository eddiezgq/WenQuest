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


async def short(ns=1):
    try:
        await Timer(ns, unit="ns")            # cocotb 2.x
    except TypeError:
        await Timer(ns, units="ns")           # cocotb 1.x


def enc_dir(dut):
    return (int(dut.uio_out.value) >> 7) & 1


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
    """刹车一拉高，PWM 在同一个时钟内变低；松开后恢复。"""
    p = await reset(dut)
    dut.ui_in.value = 128
    await ClockCycles(dut.clk, 2 * PERIOD)
    for _ in range(PERIOD):                         # wait until PWM is high
        await RisingEdge(dut.clk)
        if pwm(dut):
            break
    await short()
    assert pwm(dut) == 1, "PWM never went high at duty 128"
    p.brake = 1; p.put()
    await short()                                   # same clock: only 1 ns later, no clock edge in between
    assert pwm(dut) == 0, "PWM did not go low at once when brake was raised"
    high = 0
    for _ in range(PERIOD):                         # stays low for a whole period while braking
        await RisingEdge(dut.clk)
        high += pwm(dut)
    assert high == 0, f"PWM high for {high} clocks while braking"
    p.brake = 0; p.put()
    await ClockCycles(dut.clk, PERIOD)
    high = 0
    for _ in range(PERIOD):
        await RisingEdge(dut.clk)
        high += pwm(dut)
    assert abs(high - 4 * 128) <= 4, f"after releasing the brake: {high} high clocks, expected 512"


@cocotb.test()
async def test_encoder_steps(dut):
    """正转 40 步、反转 25 步，计数应为 15；转向输出（uio_out[7]）跟着变。提示：用上面的 step() 和 read_count()。"""
    p = await reset(dut)
    pos = await step(dut, p, 0, 40)
    c = await read_count(dut, p)
    assert c == 40 and enc_dir(dut) == 1, f"after 40 forward steps: count {c}, dir {enc_dir(dut)}"
    pos = await step(dut, p, pos, -25)
    c = await read_count(dut, p)
    assert signed16(c) == 15, f"after 40 forward and 25 reverse steps: count {signed16(c)}, expected 15"
    assert enc_dir(dut) == 0, "rotation output should be 0 (reverse) after reverse steps"
    dut._log.info("count %d, rotation %d", signed16(c), enc_dir(dut))


@cocotb.test()
async def test_glitch(dut):
    """A 相上 2 个时钟宽的毛刺不应计数。"""
    p = await reset(dut)
    # A glitch on one line would count +1 and then −1 if it were accepted, so the final count alone
    # cannot show it: watch the count (uo_out = low byte while sel = 0) on every clock as well.
    changed = 0
    for _ in range(3):                              # three 2-clock glitches on A
        p.a = 1; p.put()
        for k in range(22):
            if k == 2:
                p.a = 0; p.put()
            await RisingEdge(dut.clk)
            changed += int(dut.uo_out.value) != 0
    assert changed == 0, f"count moved during the glitches ({changed} clocks)"
    c = await read_count(dut, p)
    assert c == 0, f"2-clock glitches on A were counted: count {c}"
    pos = await step(dut, p, 0, 3)                  # real steps still count
    c = await read_count(dut, p)
    assert c == 3, f"after the glitches 3 real steps gave count {c}"


@cocotb.test()
async def test_wrap(dut):
    """从 0 反转一步，计数应为 0xFFFF（16 位回绕）。"""
    p = await reset(dut)
    await step(dut, p, 0, -1)
    c = await read_count(dut, p)
    assert c == 0xFFFF and signed16(c) == -1, f"one reverse step from 0 gave {c:#06x}, expected 0xffff"
    assert enc_dir(dut) == 0


class Motor:
    """直流电机 + 1000 线编码器模型（一阶）。每个时钟调用一次 tick(pwm, direction)。
    平均电压按每个 PWM 周期测得的占空比更新；θ 以编码器计数为单位（每转 4000 个）。"""
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
    pos = 0                                         # encoder position the chip sees

    async def run(duty, direction, ms):
        nonlocal pos
        dut.ui_in.value = duty
        p.dir = direction; p.put()
        target = 0
        for _ in range(int(ms * 1e6 / CLK_NS)):
            await RisingEdge(dut.clk)
            out = int(dut.uio_out.value)
            target = m.tick((out >> 5) & 1, (out >> 6) & 1)    # chip PWM and chip direction output
            if target != pos:                                   # at most one encoder step per clock
                pos += 1 if target > pos else -1
                p.a, p.b = GRAY[pos % 4] >> 1, GRAY[pos % 4] & 1
                p.put()
        await ClockCycles(dut.clk, 10)              # let the last step pass sync + debounce (motor frozen)
        c = signed16(await read_count(dut, p))
        return target, c

    p.brake = 0
    t1, c1 = await run(180, 1, 3)
    w1 = m.w
    dut._log.info("forward 3 ms duty 180: speed %.2f rev/s, model %d, chip %d, diff %d", w1, t1, c1, c1 - t1)
    assert abs(c1 - t1) <= 2, f"forward: chip {c1}, model {t1}"
    assert w1 > 0 and enc_dir(dut) == 1
    t2, c2 = await run(120, 0, 4)
    w2 = m.w
    dut._log.info("reverse 4 ms duty 120: speed %.2f rev/s, model %d, chip %d, diff %d", w2, t2, c2, c2 - t2)
    assert abs(c2 - t2) <= 2, f"reverse: chip {c2}, model {t2}"
    assert w2 < 0, "motor should be turning in reverse"
    assert enc_dir(dut) == 0, "rotation output should be 0 in reverse"
