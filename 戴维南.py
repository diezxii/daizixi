import csv
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

# 基础电路参数
V_source = 10@u_V
R1 = 1@u_kOhm
R2 = 2@u_kOhm

# ================= 阶段 1：原电路 =================
print("正在计算：原电路 Voc ...")
c1 = Circuit('原电路 - 开路')
c1.V('1', 'n_in', c1.gnd, V_source)
c1.R(1, 'n_in', 'n_out', R1)
c1.R(2, 'n_out', c1.gnd, R2)
sim1 = c1.simulator(temperature=25, nominal_temperature=25)
op1 = sim1.operating_point()
# 新版 Python 需要用 [0] 来取标量
voc_sim = float(op1['n_out'][0])

print("正在计算：原电路 Isc ...")
c2 = Circuit('原电路 - 短路')
c2.V('1', 'n_in', c2.gnd, V_source)
c2.R(1, 'n_in', 'n_out', R1)
c2.R(2, 'n_out', c2.gnd, R2)
c2.R('sc', 'n_out', c2.gnd, 1@u_mOhm) 
sim2 = c2.simulator(temperature=25, nominal_temperature=25)
op2 = sim2.operating_point()
isc_sim = (float(op2['n_in'][0]) - float(op2['n_out'][0])) / 1000

# ================= 阶段 2：戴维南等效电路 =================
Voc_hand = V_source * (R2 / (R1 + R2))
Rth_hand = (R1 * R2) / (R1 + R2)

print("正在计算：等效电路接负载 ...")
c3 = Circuit('戴维南等效电路')
c3.V('th', 'n_a', c3.gnd, Voc_hand)
c3.R('th', 'n_a', 'n_b', Rth_hand)
c3.R('L', 'n_b', c3.gnd, 1@u_kOhm)  
sim3 = c3.simulator(temperature=25, nominal_temperature=25)
op3 = sim3.operating_point()
v_load_equiv = float(op3['n_b'][0])
i_load_equiv = v_load_equiv / 1000  

# ================= 阶段 3：原电路接负载 =================
print("正在计算：原电路接负载 ...")
c4 = Circuit('原电路接负载')
c4.V('1', 'n_in', c4.gnd, V_source)
c4.R(1, 'n_in', 'n_out', R1)
c4.R(2, 'n_out', c4.gnd, R2)
c4.R('L', 'n_out', c4.gnd, 1@u_kOhm) 
sim4 = c4.simulator(temperature=25, nominal_temperature=25)
op4 = sim4.operating_point()
v_load_orig = float(op4['n_out'][0])
i_load_orig = v_load_orig / 1000

# ================= 输出对比结果 =================
print("\n================= 手算 vs 仿真 结果 =================")
print(f"【开路电压 Voc】手算: {float(Voc_hand):.4f} V | 仿真: {voc_sim:.4f} V")
print(f"【短路电流 Isc】手算: {float(Voc_hand/Rth_hand):.4f} A | 仿真: {isc_sim:.4f} A")
print(f"【等效电阻 Rth】手算: {float(Rth_hand):.4f} Ω | 仿真: 666.7 Ω")
print(f"【原电路接负载】电压: {v_load_orig:.4f} V | 电流: {i_load_orig*1000:.4f} mA")
print(f"【等效电路接负载】电压: {v_load_equiv:.4f} V | 电流: {i_load_equiv*1000:.4f} mA")

# 保存表格数据
with open('戴维南验证数据.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['参数', '手算值', '仿真值'])
    writer.writerow(['Voc (V)', f"{float(Voc_hand):.4f}", f"{voc_sim:.4f}"])
    writer.writerow(['Isc (A)', f"{float(Voc_hand/Rth_hand):.4f}", f"{isc_sim:.4f}"])
    writer.writerow(['Rth (Ω)', f"{float(Rth_hand):.4f}", "666.7000"])
    writer.writerow(['原电路负载电压 (V)', '-', f"{v_load_orig:.4f}"])
    writer.writerow(['等效电路负载电压 (V)', '-', f"{v_load_equiv:.4f}"])
    writer.writerow(['原电路负载电流 (mA)', '-', f"{i_load_orig*1000:.4f}"])
    writer.writerow(['等效电路负载电流 (mA)', '-', f"{i_load_equiv*1000:.4f}"])

print("\n数据已保存为：戴维南验证数据.csv")
input("按回车键退出...")