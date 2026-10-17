"""旋梭钩线的三维线环（第 37 轮“旋梭钩线”讲解，Eddie 2026-10-17 13:15：“旋梭勾线不清楚细腻，这个很难理解，即便是看实物”）。
网页虚拟样机里的线环只画在梭壳前面的一个平面里；这里按旋梭的真实转角算出线环在三维里怎样被梭尖钩住、拉大、
一边贴着梭壳前面、一边绕到梭壳后面，整个套过梭壳（里面是底线），再滑脱、被挑线杆拉上去。
坐标与虚拟样机相同：毫米，y 向上，针板面 y = 0；旋梭轴沿 x，中心 (y = YH, z = 0)；梭尖在旋梭转角 0 时位于正上方，转角增大时向 +z 走。
尺寸取自样机（第 20 轮，教材第 3–5 章）：旋梭半径 13.5（梭尖 13.75），梭壳半径 10.6、x 从 −16 到 −3.5，机针 x = −17。
这是“示意”：线的走向和先后顺序是对的，线径放大、线在梭壳上的贴合做了简化。"""
import math

XN, YH = -17.0, -21.01
R_BEAK, X_BEAK = 13.75, -14.0          # 梭尖
R_RIM = 11.4                           # 线贴着梭壳外沿走的半径（梭壳 10.6 + 线）
X_FRONT, X_BACK = -16.7, -2.8          # 前股贴梭壳前面，后股绕到梭壳后面
CATCH_TO_OFF = 270.0                   # 梭尖带着线环转 270°（主轴 135°）后脱线
SHRINK_TO = 360.0                      # 脱线后线环被拉上去，旋梭转到 360° 时收完


def ring(x, a0, a1, r, step=12.0):
    """梭壳一侧 x 面上，从旋梭转角 a0 到 a1（度）的一段圆弧点。"""
    n = max(1, int(abs(a1 - a0) / step))
    return [(x, YH + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), r * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
            for k in range(n + 1)]


def loop(phi, phc, eye, top):
    """主轴转角 phi、钩线角 phc 时，面线从针眼 eye 经梭尖回到布面 top 的路径点（不在钩线到收完这段时返回 None）。"""
    a = 2.0 * (phi - phc)                                   # 旋梭转角（度），0 = 梭尖在正上方钩线
    a = a % 720.0
    if a > SHRINK_TO:
        return None
    if a <= CATCH_TO_OFF:
        beak = math.radians(a)
        B = (X_BEAK, YH + R_BEAK * math.cos(beak), R_BEAK * math.sin(beak))
        s = 1.0
    else:                                                   # 脱线：线环离开梭尖，沿梭壳外沿继续被拉过去并收小
        u = (a - CATCH_TO_OFF) / (SHRINK_TO - CATCH_TO_OFF)
        beak = math.radians(a)
        r = R_RIM + (R_BEAK - R_RIM) * (1 - u)
        B = ((X_BEAK + (X_FRONT + X_BACK) / 2 * u) / (1 + u), YH + r * math.cos(beak), r * math.sin(beak))
        s = 1.0 - 0.7 * u
    hole = (XN + 0.3, -1.6, 0.0)
    over = (XN + 0.4, YH + R_RIM + 1.4, 0.0)                # 针板下、梭壳正上方
    front = ring(X_FRONT, 0.0, a, R_RIM) if a > 6 else []
    back = ring(X_BACK, a, 0.0, R_RIM) if a > 6 else []
    if a > CATCH_TO_OFF:                                    # 收线时两股都缩回正上方
        front = [(x, YH + (y - YH) * s + (R_RIM * (1 - s)), z * s) for x, y, z in front]
        back = [(x, YH + (y - YH) * s + (R_RIM * (1 - s)), z * s) for x, y, z in back]
    pts = [eye, (XN + 0.3, min(eye[1], 0.0) - 1.0, 0.2), hole, over] + front + [B] + back
    pts += [((X_BACK + XN) / 2, YH + R_RIM + 1.8, 0.0), (XN + 0.6, -1.4, -0.2), (XN + 0.2, 0.3, -0.1), top]
    return pts


def bobbin_thread(top):
    """底线：从梭芯（梭壳里）经梭壳前面的出线口，上到针板孔。"""
    return [(-10.0, YH, 0.0), (-15.5, YH + 4.0, -3.0), (X_FRONT + 0.2, YH + 7.5, -2.0), (XN + 0.5, -1.8, 0.0), (XN, 0.2, 0.0), top]
