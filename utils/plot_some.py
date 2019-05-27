import math
import numpy as np 
import matplotlib.pyplot as plt 

# 单进口道均衡
# inflow_light = np.array([720, 1440, 2160, 2880, 3600, 4320])
# outflow_light = np.array([782, 1177, 1360, 1364, 1365, 1376])
# avg_delay_light = np.array([31.71, 54.41, 84.97, 94.76, 92.93, 95.58])
# max_delay_light = np.array([66.34, 132.67, 132.85, 132.85, 132.95, 132.85])

# inflow_xu = np.array([720, 1440, 2160, 2880, 3600, 4320])
# outflow_xu = np.array([532, 1423, 1921, 2053, 2061, 1962])
# avg_delay_xu = np.array([3.93, 5.44, 15.04, 27.72, 29.26, 32])
# max_delay_xu = np.array([12.28, 14.09, 53.21, 56.32, 60.28, 56.72])

# inflow_dres = np.array([720, 1440, 2160, 2880, 3600, 4320])
# outflow_dres = np.array([715, 1380, 2234, 2691, 3028, 3309])
# avg_delay_dres = np.array([1.95, 2.97, 4.92, 10.47, 26.9, 29.39])
# max_delay_dres = np.array([7.01, 13.62, 21.84, 51.5, 77.6, 94.56])


# # 单进口道仅直行
# inflow_light = np.array([720, 1440, 2160, 2880, 3600])
# outflow_light = np.array([595, 1403, 2071, 2769, 3014])
# avg_delay_light = np.array([15.33, 14.76, 17.33, 27.45, 35.56])

# inflow_xu = np.array([720, 1440, 2160, 2880, 3600]) # , 4320])
# outflow_xu = np.array([693, 1346, 1933, 2000, 2156]) # , 2572])
# avg_delay_xu = np.array([3.35, 5.36, 7.32, 40.57, 54.33]) # , 54.56])

# inflow_dres = np.array([720, 1440, 2160, 2880, 3600]) # , 4320])
# outflow_dres = np.array([792, 1608, 2090, 2829, 3353]) # , 2593])
# avg_delay_dres = np.array([1.77, 2.44, 2.82, 4.39, 13.79]) # , 44.02])


# # 单进口道不均衡
# inflow_light = np.array([720, 1440, 2160, 2880, 3600])
# outflow_light = np.array([732, 1115, 948, 790, 723])
# avg_delay_light = np.array([26.61, 46.2, 73.88, 86.46, 89.4])
# max_delay_light = np.array([72.15, 118.45, 259.07, 298.125, 384.87])

# inflow_xu = np.array([720, 1440, 2160, 2880, 3600])
# outflow_xu = np.array([734, 1373, 2090, 1832, 1865])
# avg_delay_xu = np.array([3.39, 5.65, 10.74, 30.97, 29.65])
# max_delay_xu = np.array([12.77, 13.4, 33.68, 50.42, 49.72])

# inflow_dres = np.array([720, 1440, 2160, 2880, 3600])
# outflow_dres = np.array([667, 1491, 2164, 2567, 2884])
# avg_delay_dres = np.array([1.83, 3.19, 6.22, 12.82, 15.12])
# max_delay_dres = np.array([4.32, 14.42, 29.2, 43.44, 43.7])


# 三车道 均衡
inflow_light = np.array([720, 1440, 2160, 2880, 3600, 4320, 5040, 5760])
outflow_light = np.array([612, 1364, 2102, 2426, 3059, 3511, 3267, 3366])
avg_delay_light = np.array([21.34, 20.09, 23.5, 33.28, 40.48, 43.7, 55.45, 54.11])
max_delay_light = np.array([59.29, 64.97, 71.69, 109.88, 115.88, 135.89, 187, 188])

inflow_xu = np.array([720, 1440, 2160, 2880, 3600, 4320, 5040, 5760])
outflow_xu = np.array([710, 1436, 2134, 2662, 2757, 3065, 2927, 3094])
avg_delay_xu = np.array([2.19, 2.37, 5.7, 18.16, 24.41, 26.75, 39.96, 44.49])
max_delay_xu = np.array([11.66, 13.05, 23, 84.28, 80.46, 90.81, 108.2, 154.88])

inflow_dres = np.array([720, 1440, 2160, 2880, 3600, 4320, 5040, 5760])
outflow_dres = np.array([779, 1596, 2011, 3128, 3379, 4422, 5117, 5611])
avg_delay_dres = np.array([1.72, 1.96, 2.13, 2.4, 2.52, 3.93, 4.18, 7.99])
max_delay_dres = np.array([3.48, 7.36, 7.47, 17, 13.99, 35.18, 27.6, 47.29])


# # 画 flow
# plt.plot(inflow_light, outflow_light, '-o', label='traffic light')
# plt.plot(inflow_dres, outflow_dres, '-o', label='Dresner\'s')
# plt.plot(inflow_xu, outflow_xu, '-o', label='Xu\'s')
# plt.plot([0, max(inflow_xu)], [0, max(inflow_xu)], '--')
# plt.grid(True)
# # plt.axis('equal')
# plt.axis([0, math.ceil(max(inflow_xu)/1000)*1000, 0, math.ceil(max(inflow_xu)/1000)*1000])
# plt.xlabel('Theoretical inflow to intersection (veh/hour)')
# plt.ylabel('Actual outflow from intersection (veh/hour)')
# plt.title('Capacity of intersection')
# plt.legend()
# plt.show()

# 画 delay
plt.plot(inflow_light, avg_delay_light, '-o', label='traffic light')
plt.plot(inflow_dres, avg_delay_dres, '-o', label='Dresner\'s')
plt.plot(inflow_xu, avg_delay_xu, '-o', label='Xu\'s')
plt.grid(True)
plt.xlabel('Theoretical inflow to intersection (veh/hour)')
plt.ylabel('Average vehicle delay (second)')
plt.title('Average delay')
plt.legend()
plt.show()
