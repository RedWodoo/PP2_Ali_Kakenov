
import math

degree = 15
radian = degree * math.pi / 180
print("Radian:", round(radian, 6))

height = 5
base1 = 5
base2 = 6
area_trap = 0.5 * (base1 + base2) * height
print("Trapezoid area:", area_trap)

n = 4
side = 25
area_polygon = (n * side**2) / (4 * math.tan(math.pi / n))
print("Polygon area:", area_polygon)

base = 5
height = 6
area_para = base * height
print("Parallelogram area:", float(area_para))
