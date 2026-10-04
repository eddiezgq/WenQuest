"""贯通项目步骤三参考解：用 cocotb 验证电机控制芯片。

十个测试：
  test_pwm_duty        占空比 0、64、128、200、255 时，一个 PWM 周期里高电平的时钟数正好 = 4 × duty
  test_duty_mid_period 周期中途改占空比，当前周期不变，下一周期才用新值
  test_dir_output      方向输出 uio_out[6] 跟随方向命令
  test_brake           刹车一拉高，PWM 在同一个时钟内变低
  test_encoder_steps   正转 40 步、反转 25 步，计数 = 15；转向输出跟着变
  test_glitch          A、B 相上 2 个时钟宽的毛刺不计数（每个时钟都检查计数，不只看最后结果）
  test_missed_step     A、B 同时变化（跳步）不计数，err 置 1 并保持
  test_reset_position  复位时编码器停在任意一格：只作起点，不计数、不报错
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
    """Wait t nanoseconds (cocotb 2.x: unit=, 1.x: units=)."""
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


async def reset(dut, a=0, b=0, start_clock=True):
    if start_clock:
        cocotb.start_soon(clock(dut).start())
    p = Pins(dut)
    p.a, p.b = a, b
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
    await ClockCycles(dut.clk, 4)                     # back to the low byte (through the synchroniser again)
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
        assert high == 4 * duty, f"duty {duty}: {high} high clocks in a period, expected exactly {4 * duty}"
        dut._log.info("duty %d → %d/%d high clocks (%.1f %%)", duty, high, PERIOD, 100 * high / PERIOD)


@cocotb.test()
async def test_duty_mid_period(dut):
    """A new duty must wait for the next period: changing it in the middle of a period leaves that period as it was."""
    p = await reset(dut)
    dut.ui_in.value = 64
    await ClockCycles(dut.clk, 3 * PERIOD)
    while pwm(dut) == 1:                                # find the start of a period: a rising edge of pwm
        await RisingEdge(dut.clk)
    while pwm(dut) == 0:
        await RisingEdge(dut.clk)
    await ClockCycles(dut.clk, 600)                     # well past the 256 high clocks of duty 64
    dut.ui_in.value = 200
    for k in range(400):                                # rest of this period: still duty 64, so low
        await RisingEdge(dut.clk)
        assert pwm(dut) == 0, f"duty changed in the middle of a period ({600 + k} clocks after its start)"
    await ClockCycles(dut.clk, PERIOD - 1000)           # next period starts here
    high = 0
    for _ in range(PERIOD):
        await RisingEdge(dut.clk)
        high += pwm(dut)
    assert high == 800, f"the next period should have duty 200 (800 high clocks), got {high}"


@cocotb.test()
async def test_dir_output(dut):
    """The H-bridge direction pin uio_out[6] follows the direction command."""
    p = await reset(dut)
    for d in (1, 0, 1):
        p.dir = d; p.put()
        await ClockCycles(dut.clk, 4)
        assert (int(dut.uio_out.value) >> 6) & 1 == d


@cocotb.test()
async def test_brake(dut):
    p = await reset(dut)
    dut.ui_in.value = 255
    await ClockCycles(dut.clk, 2 * PERIOD)
    assert pwm(dut) == 1
    p.brake = 1; p.put()
    await ns(1)
    assert pwm(dut) == 0, "PWM must drop as soon as brake is high"
    await ClockCycles(dut.clk, PERIOD)
    assert pwm(dut) == 0
    p.brake = 0; p.put()
    await ClockCycles(dut.clk, 4)
    assert pwm(dut) == 1


@cocotb.test()
async def test_encoder_steps(dut):
    p = await reset(dut)
    pos = await step(dut, p, 0, 40)
    assert signed16(await read_count(dut, p)) == 40
    assert (int(dut.uio_out.value) >> 7) & 1 == 1, "rotation output should say forward"
    pos = await step(dut, p, pos, -25)
    assert signed16(await read_count(dut, p)) == 15
    assert (int(dut.uio_out.value) >> 7) & 1 == 0, "rotation output should say reverse"


@cocotb.test()
async def test_glitch(dut):
    """2-clock spikes on A and on B must never change the count — checked at every clock, because a counted
    spike adds one and then subtracts one, so looking only at the final count would miss it."""
    p = await reset(dut)
    await step(dut, p, 0, 8)
    before = await read_count(dut, p)                 # sel = 0: uo_out shows the low byte from here on
    await ClockCycles(dut.clk, 4)
    for line, width in (("a", 2), ("b", 2), ("a", 4), ("b", 4)):
        setattr(p, line, getattr(p, line) ^ 1); p.put()
        await ClockCycles(dut.clk, width)               # 100 ns and 200 ns spikes (shorter than the filter)
        setattr(p, line, getattr(p, line) ^ 1); p.put()
        for _ in range(30):
            await RisingEdge(dut.clk)
            assert int(dut.uo_out.value) == before & 0xFF, f"a {width}-clock glitch on {line.upper()} changed the count"
    assert await read_count(dut, p) == before


@cocotb.test()
async def test_missed_step(dut):
    """A and B changing together (a step was missed) must not be counted, and err goes to 1 and stays."""
    p = await reset(dut)
    pos = await step(dut, p, 0, 4)                      # back at state 00
    before = await read_count(dut, p)
    p.a, p.b = 1, 1; p.put()                            # 00 → 11 in one go
    await ClockCycles(dut.clk, 20)
    assert await read_count(dut, p) == before, "a missed step must not change the count"
    assert int(dut.u_dec.err.value) == 1, "err must be set on a missed step"
    await step(dut, p, 2, 1)                            # carry on normally from 11
    assert int(dut.u_dec.err.value) == 1, "err stays set until reset"


@cocotb.test()
async def test_reset_position(dut):
    """The encoder may stand at any state at reset: that state is only the starting point (no count, no error)."""
    for k, (a, b, start) in enumerate(((1, 0, 1), (1, 1, 2), (0, 1, 3))):
        p = await reset(dut, a, b, start_clock=(k == 0))
        await ClockCycles(dut.clk, 20)
        assert await read_count(dut, p) == 0, f"reset with (A,B) = ({a},{b}) must leave the count at 0"
        assert int(dut.u_dec.err.value) == 0, f"reset with (A,B) = ({a},{b}) must not flag an error"
        await step(dut, p, start, 3)
        assert signed16(await read_count(dut, p)) == 3


@cocotb.test()
async def test_wrap(dut):
    p = await reset(dut)
    await step(dut, p, 0, -1)
    assert await read_count(dut, p) == 0xFFFF


@cocotb.test()
async def test_motor(dut):
    """PWM → DC motor model → encoder → chip count; the count must follow the shaft angle."""
    p = await reset(dut)
    TAU, KV, VBUS, LINES = 0.5e-3, 50.0 / 12.0, 12.0, 1000      # τ (s), rev/s per volt, bus volts, encoder lines
    dt = CLK_NS * 1e-9
    w = 0.0                     # rev/s
    theta = 0.0                 # encoder counts (4 per line)
    pos = 0
    high = 0
    v_avg = 0.0
    log = []

    async def run(duty, direction, clocks):
        nonlocal w, theta, pos, high, v_avg
        dut.ui_in.value = duty
        p.dir = direction; p.put()
        for k in range(clocks):
            await RisingEdge(dut.clk)
            high += pwm(dut)
            if k % PERIOD == PERIOD - 1:              # update the motor once per PWM period from the measured duty
                v_avg = high / PERIOD * VBUS * (1 if direction else -1)
                high = 0
            w += (KV * v_avg - w) / TAU * dt
            theta += w * 4 * LINES * dt
            target = math.floor(theta)
            if target != pos:                          # at most one quadrature step per clock (well below the filter limit here)
                pos += 1 if target > pos else -1
                p.a, p.b = GRAY[pos % 4] >> 1, GRAY[pos % 4] & 1
                p.put()
            if k % 2000 == 0:
                log.append((round(w, 1), pos))

    await run(180, 1, 60000)                           # 3 ms forward
    c1 = signed16(await read_count(dut, p))
    dut._log.info("forward: speed %.1f rev/s, shaft %d counts, chip %d", w, pos, c1)
    assert abs(c1 - pos) <= 2, f"chip counted {c1}, shaft moved {pos}"
    assert w > 0.9 * KV * 180 / 256 * VBUS * 0.95, "motor should be near its steady speed"
    await run(120, 0, 80000)                           # 4 ms reverse command: slows down, turns back
    c2 = signed16(await read_count(dut, p))
    dut._log.info("reverse: speed %.1f rev/s, shaft %d counts, chip %d", w, pos, c2)
    assert w < 0, "motor should be turning backwards"
    assert abs(c2 - pos) <= 2, f"chip counted {c2}, shaft moved {pos}"
    assert (int(dut.uio_out.value) >> 7) & 1 == 0
