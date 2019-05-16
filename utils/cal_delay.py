import csv
import sys
sys.path.append("../") # cd 到 utils 文件夹外面再执行
from lib.settings import veh_param, cf_param, inter_v_lim, arm_len, veh_dt

import numpy as np
import matplotlib.pyplot as plt

def cal_delay(fname):
    file = open(fname)
    reader = csv.reader(file)
    # 列分别是 start_time, ju_track_len, removed_time, is_removed
    veh_info_table = - np.ones((500, 4))
    for i, row in enumerate(reader):
        if i == 0 or row[0].startswith('[') or row[0].startswith('p'):
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
    print('avg_delay = %.2f' % np.mean(delay))
    print('max_delay = %.2f' % np.max(delay))
    plt.plot(delay)
    plt.show()

def see_veh_avx(fname, id):
    file = open(fname)
    reader = csv.reader(file)
    x_ap = []
    t_ap = []
    x_ju = []
    t_ju = []
    x_ex = []
    t_ex = []
    for i, row in enumerate(reader):
        if i == 0:
            continue
        t, veh_id, zone, x = int(row[0]), int(row[1]), row[2].strip(), float(row[4])
        if id != veh_id:
            continue
        if zone == 'ap':
            t_ap.append(t * veh_dt)
            x_ap.append(x)
        elif zone == 'ju':
            t_ju.append(t * veh_dt)
            x_ju.append(x)
        else:
            t_ex.append(t * veh_dt)
            x_ex.append(x)
    
    v_ap = [(x_ap[i+1] - x_ap[i])/veh_dt for i in range(len(x_ap)-1)]
    a_ap = [(v_ap[i+1] - v_ap[i])/veh_dt for i in range(len(v_ap)-1)]
    v_ju = [(x_ju[i+1] - x_ju[i]) for i in range(len(x_ju)-1)]
    a_ju = [(v_ju[i+1] - v_ju[i]) for i in range(len(v_ju)-1)]
    plt.subplot(321)
    plt.plot(t_ap, x_ap)
    plt.subplot(322)
    plt.plot(t_ju, x_ju)
    plt.subplot(323)
    plt.plot(t_ap[:-1], v_ap)
    plt.subplot(324)
    plt.plot(t_ju[:-1], v_ju)
    plt.subplot(325)
    plt.plot(t_ap[:-2], a_ap)
    plt.subplot(326)
    plt.plot(t_ju[:-2], a_ju)
    plt.show()

if __name__ == '__main__':
    fname = '../log/log 2019-05-16 11-18-41.log'
    cal_delay(fname)
    # see_veh_avx(fname, 70)

