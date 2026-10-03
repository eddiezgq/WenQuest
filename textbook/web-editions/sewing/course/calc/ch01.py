"""Chapter 1 (sewing equipment and the apparel industry): numbers used in course/lessons/ch01.json."""
import math
# needle-bar worked example of Chapter 3: m = 120 g, r = 15.5 mm, l = 55 mm
r, l, m = 15.5, 55.0, 0.120
lam = r / l
def a_bdc(n):
    w = 2 * math.pi * n / 60
    return r / 1000 * w * w * (1 + lam)          # exact at BDC: r w^2 (1 + lambda)
for n in (200, 1000, 3000, 4000, 5000, 6000):
    print(f"n={n:5d}: a_BDC={a_bdc(n):8.1f} m/s^2, F={m*a_bdc(n):7.1f} N, reversals per s={n/60:.1f}")
print("textbook a200 = 5450*(200/5000)^2 =", round(5450 * (200 / 5000) ** 2, 2))
print("ratio 5000 vs 200:", (5000 / 200) ** 2)
print("5000 -> 6000 increase:", round(((6000 / 5000) ** 2 - 1) * 100), "%")
print("4000 -> 5000 increase:", round(((5000 / 4000) ** 2 - 1) * 100, 1), "%")
print("F 6000 from textbook value 654*1.44 =", round(654 * 1.44))
print("F 4000 = 654*(4000/5000)^2 =", round(654 * (4000/5000)**2))
print("F 3000 = 654*(3000/5000)^2 =", round(654 * (3000/5000)**2))
# industry numbers (textbook 1.5)
prod, exp_units, exp_usd = 685e4, 469e4, 15.22e8
print("export share of output 2024:", round(exp_units / prod * 100, 1), "%")
print("average export value per machine:", round(exp_usd / exp_units, 1), "USD")
print("2023 output implied by +22%:", round(prod / 1.22 / 1e4), "x10^4")
print("China apparel+footwear exports 2020:", round(5835 * 0.308), "x10^8 USD")
print("world output if China = 70%..80%:", round(prod / 0.8 / 1e4), "-", round(prod / 0.7 / 1e4), "x10^4")
print("ILO: women in garment ~80%")
# patent pool 1856-1877
print("pool years:", 1877 - 1856)
# Howe patent 1846 -> Singer 1851
print("Howe->Singer:", 1851 - 1846, "years; Thimonnier 1830 -> Gibbs 1857:", 1857 - 1830)
# Thimonnier 200 st/min vs 5000 st/min: time per stitch
print("time per stitch 200:", 60 / 200 * 1000, "ms; 5000:", 60 / 5000 * 1000, "ms")
