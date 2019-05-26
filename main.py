import sys
import time
import logging

import lib.settings

def exec_simulation():
    from PyQt5.QtWidgets import QApplication
    from my_main_window import MyMainWindow
    from cal_delay import cal_metrics

    log_fname = 'log/log %s.log' % time.strftime("%Y-%m-%d %H-%M-%S")
    logging.basicConfig(filename=log_fname, format='%(message)s', level=logging.DEBUG)
    logging.debug('t, veh._id, zone, lane, x, v, a')
    print(log_fname)

    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    app.exec_()

    metrics = cal_metrics(log_fname)
    for key, value in metrics.items():
        print(key, '=', value)
    print('')

if __name__ == '__main__':
    # 调整方案
    mode = sys.argv[1]
    if mode == 'Dresner':
        lib.settings.arm_len = 100
        lib.settings.inter_control_mode = 'Dresner'
    elif mode == 'Xu':
        lib.settings.arm_len = 200
        lib.settings.inter_control_mode = 'Xu'
    else:
        lib.settings.arm_len = 100
        lib.settings.inter_control_mode = 'traffic light'

    # 调整流量
    total_flow = int(sys.argv[2])
    # 一车道只直
    t_flow = total_flow / 4
    # # 均衡
    # l_flow = total_flow / 16
    # t_flow = total_flow / 8
    # r_flow = total_flow / 16
    # # 不均衡
    # N_flow = total_flow / 9
    # S_flow = total_flow / 9 * 2
    # E_flow = total_flow / 9 * 2
    # W_flow = total_flow / 9 * 4

    lib.settings.veh_gen_rule_table = {
        # 一车道只直
        'Nl': [0], 
        'Nt': [t_flow], 
        'Nr': [0], 
        'Sl': [0], 
        'St': [t_flow], 
        'Sr': [0], 
        'El': [0], 
        'Et': [t_flow], 
        'Er': [0], 
        'Wl': [0], 
        'Wt': [t_flow], 
        'Wr': [0]
    }
    print('## %d = 4 * %d' % (total_flow, t_flow))
    print(lib.settings.veh_gen_rule_table)

    exec_simulation()

