import csv
import sys
sys.path.append("../") # cd 到 utils 文件夹再执行
from lib.settings import veh_param, cf_param, inter_v_lim, arm_len, veh_dt

import numpy as np
import matplotlib.pyplot as plt

fname = '../log/log 2019-05-14 11-20-53.log'
file = open(fname)
reader = csv.reader(file)
# 列分别是 start_time, ju_track_len, removed_time, is_removed
veh_info_table = - np.ones((500, 4))
for i, row in enumerate(reader):
    if i == 0:
        continue
    t, veh_id, zone, x = int(row[0]), int(row[1]), row[2].strip(), float(row[4])
    if zone == 'ap':
        if veh_info_table[veh_id, 0] == -1:
            veh_info_table[veh_id, 0] = t
    if zone == 'ju':
        veh_info_table[veh_id, 1] = max(veh_info_table[veh_id, 1], x)
    if zone == 'ex':
        veh_info_table[veh_id, 2] = max(veh_info_table[veh_id, 2], t)
        if x >= arm_len + (veh_param['veh_len'] - veh_param['veh_len_front']):
            veh_info_table[veh_id, 3] = 1

veh_not_finish_min = np.where(veh_info_table[:, 3] < 0)[0][0] # 最小的没有完成全程的车辆
print('veh_not_finish_min = %d' % veh_not_finish_min)
veh_info_table = veh_info_table[0: veh_not_finish_min, :]

# 实际时间
actual_time = (veh_info_table[:, 2] - veh_info_table[:, 0]) * veh_dt
# 理想通行时间，由匀速-减速-匀速-加速-匀速组成
ideal_time = (arm_len - (cf_param['v0']**2 - inter_v_lim**2) / 2 / veh_param['max_dec']) / cf_param['v0'] + \
    (cf_param['v0'] - inter_v_lim) / veh_param['max_dec'] + \
    veh_info_table[:, 1] / inter_v_lim + \
    (cf_param['v0'] - inter_v_lim) / veh_param['max_acc'] + \
    (arm_len - (cf_param['v0']**2 - inter_v_lim**2) / 2 / veh_param['max_acc']) / cf_param['v0']
delay = actual_time - ideal_time
# print(delay)
print('avg_delay = %.2f' % np.mean(delay))
print('max_delay = %.2f' % np.max(delay))
plt.plot(delay)
plt.show()



