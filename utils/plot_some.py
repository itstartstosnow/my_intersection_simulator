import math
import numpy as np 
import matplotlib
import matplotlib.pyplot as plt 

# # 单进口道均衡
# inflow_light = np.array([720, 1440, 2160, 2880]) #, 3600, 4320])
# outflow_light = np.array([749, 1189, 1440, 1560, 1494, 1541])
# avg_delay_light = np.array([21.20, 52.33, 82.14, 86.8]) #, 87.3, 86.45])

# inflow_xu = np.array([720, 1440, 2160, 2880]) #, 3600, 4320])
# outflow_xu = np.array([532, 1423, 1921, 2053, 2061, 1962])
# avg_delay_xu = np.array([3.93, 5.44, 15.04, 27.72]) #, 29.26, 32])
# max_delay_xu = np.array([12.28, 14.09, 53.21, 56.32, 60.28, 56.72])

# inflow_dres = np.array([720, 1440, 2160, 2880, 3600, 4320])
# outflow_dres = np.array([715, 1380, 2234, 2691, 3028, 3309])
# avg_delay_dres = np.array([1.95, 2.97, 4.92, 10.47, 26.9, 29.39])
# max_delay_dres = np.array([7.01, 13.62, 21.84, 51.5, 77.6, 94.56])


# # # # 单进口道仅直行
# inflow_light = np.array([720, 1440, 2160, 2880, 3600])
# outflow_light = np.array([687, 1426, 2076, 2570, 2845])
# avg_delay_light = np.array([7.42, 10.7, 14.67, 27.9, 34.71])

# inflow_xu = np.array([720, 1440, 2160, 2880, 3600])
# outflow_xu = np.array([693, 1346, 1933, 2000, 2156])
# avg_delay_xu = np.array([3.35, 5.36, 7.32, 40.57, 54.33])

# inflow_dres = np.array([720, 1440, 2160, 2880, 3600])
# outflow_dres = np.array([792, 1608, 2090, 2829, 3353])
# avg_delay_dres = np.array([1.77, 2.44, 2.82, 4.39, 13.79])


# # 单进口道不均衡
# inflow_light = np.array([720, 1440, 2160, 2880, 3600])
# outflow_light = np.array([640, 1087, 1250, 990, 938])
# avg_delay_light = np.array([22.07, 41.97, 75.77, 76.51, 82.11])

# inflow_xu = np.array([720, 1440, 2160, 2880, 3600])
# outflow_xu = np.array([734, 1373, 2090, 1832, 1865])
# avg_delay_xu = np.array([3.39, 5.65, 10.74, 30.97, 29.65])
# max_delay_xu = np.array([12.77, 13.4, 33.68, 50.42, 49.72])

# inflow_dres = np.array([720, 1440, 2160, 2880, 3600])
# outflow_dres = np.array([667, 1491, 2164, 2567, 2884])
# avg_delay_dres = np.array([1.83, 3.19, 6.22, 12.82, 15.12])
# max_delay_dres = np.array([4.32, 14.42, 29.2, 43.44, 43.7])


# 三车道 均衡
inflow_light = np.array([720, 1440, 2160, 2880, 3600, 4320]) #, 5040, 5760])
outflow_light = np.array([646, 1452, 1958, 2341, 2868, 3270, 3436, 3674])
avg_delay_light = np.array([11.32, 17.72, 17.94, 34.22, 42.08, 44.58]) #, 51.29, 57.53])

inflow_xu = np.array([720, 1440, 2160, 2880, 3600, 4320]) #, 5040, 5760])
outflow_xu = np.array([710, 1436, 2134, 2662, 2757, 3065, 2927, 3094])
avg_delay_xu = np.array([2.19, 2.37, 5.7, 18.16, 24.41, 26.75]) #, 39.96, 44.49])
max_delay_xu = np.array([11.66, 13.05, 23, 84.28, 80.46, 90.81, 108.2, 154.88])

inflow_dres = np.array([720, 1440, 2160, 2880, 3600, 4320, 5040, 5760])
outflow_dres = np.array([779, 1596, 2011, 3128, 3379, 4422, 5117, 5611])
avg_delay_dres = np.array([1.72, 1.96, 2.13, 2.4, 2.52, 3.93, 4.18, 7.99])
max_delay_dres = np.array([3.48, 7.36, 7.47, 17, 13.99, 35.18, 27.6, 47.29])

font_ch = matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\YaHei Consolas Hybrid 1.12.ttf')

# # 画 flow
# plt.plot(inflow_light, outflow_light, '-o', label='信号控制')
# plt.plot(inflow_dres, outflow_dres, '-o', label='Dresner方案')
# plt.plot(inflow_xu, outflow_xu, '-o', label='Xu方案')
# # plt.plot([0, max(inflow_xu)], [0, max(inflow_xu)], '--')
# plt.grid(True)
# # plt.axis('equal')
# plt.axis([0, math.ceil(max(inflow_dres)/1000)*1000, 0, math.ceil(max(inflow_dres)/1000)*1000])
# plt.xlabel('仿真输入流量 (pcu/hour)', fontproperties=font_ch)
# plt.ylabel('实际流出流量 (pcu/hour)', fontproperties=font_ch)
# plt.title('通行能力', fontproperties=font_ch)
# plt.legend(prop=font_ch)
# plt.show()

# 画 delay
plt.plot(inflow_light, avg_delay_light, '-o', label='信号控制')
plt.plot(inflow_dres, avg_delay_dres, '-o', label='Dresner方案')
plt.plot(inflow_xu, avg_delay_xu, '-o', label='Xu方案')
# plt.plot(inflow_light_1b, avg_delay_light_1b, '--o', color='C0', label='traffic light, scene 1')
# plt.plot(inflow_light_1ot, avg_delay_light_1ot, '-^', color='C0', label='traffic light, scene 2')
# plt.plot(inflow_dres_1b, avg_delay_dres_1b, '--o', color='C1', label='Dresner\'s, scene 1')
# plt.plot(inflow_dres_1ot, avg_delay_dres_1ot, '-^', color='C1', label='Dresner\'s, scene 2')
# plt.plot(inflow_xu_1b, avg_delay_xu_1b, '--o', color='C2', label='Xu\'s, scene 1')
# plt.plot(inflow_xu_1ot, avg_delay_xu_1ot, '-^', color='C2', label='Xu\'s, scene 2')
plt.grid(True)
plt.axis([0, math.ceil(max(inflow_dres)/1000)*1000, 0, 100])
plt.xlabel('仿真输入流量 (pcu/hour)', fontproperties=font_ch)
plt.ylabel('平均延误 (s)', fontproperties=font_ch)
plt.title('平均延误', fontproperties=font_ch)
plt.legend(prop=font_ch)
plt.show()
