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
    # # 均衡
    # l_flow = total_flow / 16
    # t_flow = total_flow / 8
    # r_flow = total_flow / 16
    # 不均衡
    N_flow = total_flow / 9
    S_flow = total_flow / 9 * 2
    E_flow = total_flow / 9 * 2
    W_flow = total_flow / 9 * 4
    lib.settings.veh_gen_rule_table = {
        # # 一车道均衡
        # 'Nl': [l_flow], 
        # 'Nt': [t_flow], 
        # 'Nr': [r_flow], 
        # 'Sl': [l_flow], 
        # 'St': [t_flow], 
        # 'Sr': [r_flow], 
        # 'El': [l_flow], 
        # 'Et': [t_flow], 
        # 'Er': [r_flow], 
        # 'Wl': [l_flow], 
        # 'Wt': [t_flow], 
        # 'Wr': [r_flow]
        # 一车道不均衡
        'Nl': [N_flow/4], 
        'Nt': [N_flow/2], 
        'Nr': [N_flow/4], 
        'Sl': [S_flow/4], 
        'St': [S_flow/2], 
        'Sr': [S_flow/4], 
        'El': [E_flow/4], 
        'Et': [E_flow/2], 
        'Er': [E_flow/4], 
        'Wl': [W_flow/4], 
        'Wt': [W_flow/2], 
        'Wr': [W_flow/4]
        # # 三车道
        # 'Nl': [l_flow, 0, 0], 
        # 'Nt': [0, t_flow, 0], 
        # 'Nr': [0, 0, r_flow], 
        # 'Sl': [l_flow, 0, 0], 
        # 'St': [0, t_flow, 0],
        # 'Sr': [0, 0, r_flow],
        # 'El': [l_flow, 0, 0], 
        # 'Et': [0, t_flow, 0],
        # 'Er': [0, 0, r_flow],
        # 'Wl': [l_flow, 0, 0], 
        # 'Wt': [0, t_flow, 0],
        # 'Wr': [0, 0, r_flow]
    }
    print('## %d = %d + %d + %d + %d' % (total_flow, N_flow,  S_flow, E_flow, W_flow))
    print(lib.settings.veh_gen_rule_table)

    exec_simulation()

