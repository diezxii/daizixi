import csv
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

# 1. 建立 NMOS 共源级放大电路
circuit = Circuit('NMOS Common Source Amplifier')

# 直流电源 VDD = 5V
circuit.V('DD', 'vdd', circuit.gnd, 5@u_V)

# 栅极分压电阻 Rg1=60k, Rg2=40k
circuit.R('g1', 'vdd', 'g', 60@u_kOhm)
circuit.R('g2', 'g', circuit.gnd, 40@u_kOhm)

# 漏极电阻 Rd=2k
circuit.R('d', 'vdd', 'd', 2@u_kOhm)

# 输入交流信号：10mV / 1kHz
circuit.SinusoidalVoltageSource('in', 'vin', circuit.gnd, amplitude=10@u_mV, frequency=1@u_kHz)

# 输入耦合电容 Cb1（10uF 足以视为交流短路）
circuit.C('b1', 'vin', 'g', 10@u_uF)

# NMOS 模型（参数按题目要求）
circuit.MOSFET(1, 'd', 'g', circuit.gnd, circuit.gnd, model='nmos_model')
circuit.model('nmos_model', 'NMOS', level=1, KP=0.8e-3, VTO=1, LAMBDA=0.02)

simulator = circuit.simulator(temperature=25, nominal_temperature=25)

# 2. 直流工作点分析
print("正在计算直流工作点...")
op = simulator.operating_point()
vgs = float(op['g'][0])
id_current = (5 - float(op['d'][0])) / 2000  # I_D = (VDD - V_D) / Rd
vds = float(op['d'][0])
print(f"【仿真】V_GS = {vgs:.4f} V")
print(f"【仿真】I_D  = {id_current*1000:.4f} mA")
print(f"【仿真】V_DS = {vds:.4f} V")

# 3. 瞬态分析（看波形）
print("正在计算瞬态波形...")
analysis = simulator.transient(step_time=10@u_us, end_time=3@u_ms)

with open('NMOS_瞬态数据.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['时间(ms)', '输入电压(mV)', '输出电压(V)'])
    for i in range(len(analysis.time)):
        t = float(analysis.time[i]) * 1000
        vin = float(analysis['vin'][i]) * 1000  # 转 mV
        vout = float(analysis['d'][i])
        if i % 50 == 0:
            writer.writerow([f"{t:.4f}", f"{vin:.4f}", f"{vout:.4f}"])

print("\n数据已保存为：NMOS_瞬态数据.csv")
input("按回车键退出...")