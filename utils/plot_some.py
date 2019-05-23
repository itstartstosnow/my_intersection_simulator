
import numpy as np 
import matplotlib.pyplot as plt 

# inflow_light = np.array([720, 1440, 2880])
# outflow_light = np.array([634, 1218, 1363])
# avg_delay_light = np.array([27.79, 30.77, 45.44])
# max_delay_light = np.array([50.67, 66.07, 99.80])

# inflow_xu = np.array([720, 1440, 2880, 4320])
# outflow_xu = np.array([840, 1586, 2150, 2057])
# avg_delay_xu = np.array([3.17, 6.31, 16.46, 28.05])
# max_delay_xu = np.array([11.64, 14.74, 42.32, 56.20])

# inflow_dres = np.array([720, 1440, 2880, 4320])
# outflow_dres = np.array([735, 1330, 2177, 2792])
# avg_delay_dres = np.array([1.76, 2.98, 6.36, 21.58])
# max_delay_dres = np.array([4.32, 13.61, 30.32, 61.90])


inflow_light = np.array([720, 1440, 2880])
outflow_light = np.array([631, 661, 819])
avg_delay_light = np.array([38.17, 31.00, 38.23])
max_delay_light = np.array([76.27, 72.75, 81.33])

inflow_xu = np.array([720, 1440, 2880, 3600])
outflow_xu = np.array([544, 1541, 3050, 2529])
avg_delay_xu = np.array([3.78, 6.53, 10.90, 18.85])
max_delay_xu = np.array([9.32, 13.77, 27.32, 43.99])

inflow_dres = np.array([720, 1440, 2880, 3600])
outflow_dres = np.array([769, 1420, 2558, 2921])
avg_delay_dres = np.array([1.81, 2.98, 6.73, 14.14])
max_delay_dres = np.array([5.41, 9.12, 20.12, 34.58])


# plt.plot(inflow_light, outflow_light, '-o', label='traffic light')
# plt.plot(inflow_dres, outflow_dres, '-o', label='Dresner\'s')
# plt.plot(inflow_xu, outflow_xu, '-o', label='Xu\'s')
# plt.xlabel('Theoretical inflow to intersection (veh/hour)')
# plt.ylabel('Actual outflow from intersection (veh/hour)')
# plt.title('Capacity of intersection')
# plt.legend()
# plt.show()

plt.plot(inflow_light, avg_delay_light, '-o', label='traffic light')
plt.plot(inflow_dres, avg_delay_dres, '-o', label='Dresner\'s')
plt.plot(inflow_xu, avg_delay_xu, '-o', label='Xu\'s')
plt.xlabel('Theoretical inflow to intersection (veh/hour)')
plt.ylabel('Average vehicle delay (second)')
plt.title('Average delay')
plt.legend()
plt.show()

inflow_xu = np.array([])