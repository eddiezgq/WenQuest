"""贯通项目步骤三参考解：用 cocotb 验证电机控制芯片。

六个测试：
  test_pwm_duty        占空比 0、64、128、200、255 时，一个 PWM 周期里高电平的时钟数 = 4 × duty
  test_brake           刹车一拉高，PWM 在同一个时钟内变低
  test_encoder_steps   正转 40 步、反转 25 步，计数 = 15；转向输出跟着变
  test_glitch          A、B 相上 2 个时钟宽的毛刺不计数（每个时钟都检查计数，不只看最后结果）
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
    for line in ("a", "b"):
        setattr(p, line, getattr(p, line) ^ 1); p.put()
        await ClockCycles(dut.clk, 2)                   # 100 ns spike
        setattr(p, line, getattr(p, line) ^ 1); p.put()
        for _ in range(30):
            await RisingEdge(dut.clk)
            assert int(dut.uo_out.value) == before & 0xFF, f"a 2-clock glitch on {line.upper()} changed the count"
    assert await read_count(dut, p) == before


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
