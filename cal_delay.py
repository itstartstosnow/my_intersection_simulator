import csv
import sys
from lib.settings import veh_param, cf_param, inter_v_lim, arm_len, veh_dt, simu_t

import numpy as np
import matplotlib.pyplot as plt

def cal_metrics(fname):
    file = open(fname)
    reader = csv.reader(file)

    # 列分别是 start_time, ju_track_len, removed_time, is_removed
    veh_info_table = - np.ones((2000, 4))
    for i, row in enumerate(reader):
        if i == 0 or row[0].startswith('[') or row[0].startswith('p'):
            continue
        if row[0].startswith('update_title_pos'):
            break
        t, veh_id, zone, x = int(row[0]), int(row[1]), row[2].strip(), float(row[4])
        if t >= simu_t / veh_dt:
            break
        if zone == 'ap':
            if veh_info_table[veh_id, 0] == -1:
                veh_info_table[veh_id, 0] = t
        if zone == 'ju':
            veh_info_table[veh_id, 1] = max(veh_info_table[veh_id, 1], x)
        if zone == 'ex':
            veh_info_table[veh_id, 2] = max(veh_info_table[veh_id, 2], t)
            if x >= arm_len + (veh_param['veh_len'] - veh_param['veh_len_front']):
                veh_info_table[veh_id, 3] = 1

    metrics = {}

    # 找到最小的没有完成全程的车辆
    veh_not_finish_min = np.where(veh_info_table[:, 3] < 0)[0][0] # 最小的没有完成全程的车辆
    metrics['veh_not_finish_min'] = veh_not_finish_min
    veh_info_table = veh_info_table[0: veh_not_finish_min, :]

    # 计算实际通行能力（从第一辆车离开到最后一辆车离开交叉口时间内的流量）
    veh_finish_count = np.sum(veh_info_table[:, 3]) # 完成全程的车辆数
    earlist_finish_time = np.min(veh_info_table[:, 2]) # 最早完成全程的时间
    actual_total_flow = veh_finish_count / (simu_t - earlist_finish_time * veh_dt) * 3600
    metrics['actual_total_flow'] = actual_total_flow

    # 计算延误
    # 实际时间
    actual_time = (veh_info_table[:, 2] - veh_info_table[:, 0]) * veh_dt
    # 理想通行时间，无视交叉口和其它车辆，匀速通过
    ideal_time = (arm_len * 2 + veh_info_table[:, 1]) / cf_param['v0']
    delay = actual_time - ideal_time
    metrics['avg_delay'] = np.mean(delay)
    metrics['max_delay'] = np.max(delay)

    plt.plot(delay)
    plt.xlabel('Vehicle Id')
    plt.ylabel('Delay / s')
    plt.grid(True)
    plt.savefig(fname[:-4]+'.png')

    return metrics

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

    files = [
        'log 2019-05-25 14-55-14.log', 
        'log 2019-05-25 14-58-27.log', 
        'log 2019-05-25 15-01-40.log', 
        'log 2019-05-25 15-05-00.log', 
        'log 2019-05-25 15-08-27.log', 
        'log 2019-05-25 15-11-58.log', 
        'log 2019-05-25 15-26-54.log', 
        'log 2019-05-25 15-32-04.log', 
        'log 2019-05-25 16-04-54.log', 
        'log 2019-05-25 16-37-04.log', 
        'log 2019-05-25 16-42-24.log', 
        'log 2019-05-25 16-48-41.log', 
        'log 2019-05-25 16-52-46.log', 
        'log 2019-05-25 16-55-58.log', 
        'log 2019-05-25 16-59-11.log', 
        'log 2019-05-25 17-09-25.log'
    ]

    for file in files:
        metrics = cal_metrics('log/3_10min/3lanes_banlanced/' + file)
        print(file)
        for key, value in metrics.items():
            print(key, '=', value)
        print('')

