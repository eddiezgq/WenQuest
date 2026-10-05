"""本章共用的模拟测量数据（固定随机种子，正文、图、程序用同一份）。以下划线开头，构建时不单独运行。"""
import numpy as np

# (a) 夹爪手指的力–变形：F = k δ + F0，k = 2.4 N/mm，预紧力 F0 = 1.5 N，力传感器噪声 0.3 N
rng = np.random.default_rng(1005)
delta = np.linspace(0.0, 5.0, 11)                 # mm
force = 2.4 * delta + 1.5 + rng.normal(scale=0.3, size=delta.size)

# (b) 力传感器零点随温度漂移（N）：真实曲线 + 噪声；训练用 12 个温度点，检验用另外 12 个
def drift_true(T):
    x = (T - 40.0) / 20.0
    return 0.20 + 0.35 * x - 0.25 * x ** 2 + 0.30 * x ** 3


rng2 = np.random.default_rng(2024)
T_train = np.linspace(20.0, 60.0, 12)
T_test = np.sort(rng2.uniform(20.0, 60.0, 12))
y_train = drift_true(T_train) + rng2.normal(scale=0.03, size=12)
y_test = drift_true(T_test) + rng2.normal(scale=0.03, size=12)

# (c) 关节摩擦辨识：τ = I α + b ω + c sign(ω)，I = 0.05 kg·m²，b = 0.12 N·m·s/rad，c = 0.8 N·m
rng3 = np.random.default_rng(7)
t = np.linspace(0.0, 6.0, 300)
omega = 1.5 * np.sin(1.3 * t) + 0.6 * np.sin(3.1 * t + 0.4)
alpha = 1.5 * 1.3 * np.cos(1.3 * t) + 0.6 * 3.1 * np.cos(3.1 * t + 0.4)
tau = 0.05 * alpha + 0.12 * omega + 0.8 * np.sign(omega) + rng3.normal(scale=0.05, size=t.size)
