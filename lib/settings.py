########################## 全局步长设置 ##########################
veh_dt = 0.1
disp_dt = 0.04

########################## 场景参数设置 ##########################
lane_width = 3.5
turn_radius = 6 # 美国城市街道设计指南要求一般城市道路交叉口转角半径采用3~4.5m
arm_len = 100
NS_lane_count = 3
EW_lane_count = 3
arm_v_lim = 16.66    # 60 km/h
inter_v_lim = 11.11  # 交叉口区域的限速

########################## 车辆参数设置 ##########################
veh_param = {
    'veh_wid': 2,
    'veh_len': 4.8,
    'veh_len_front': 1,      # 前保险杠到前轮轴的距离
    'max_v': 33,
    'max_acc': 3,
    'max_dec': 6,
    'ap_arm': None,
    'ap_lane': None,
    'turn_dir': None
}

cf_param = {
    'v0': 15,    # 54 km/h，符合一般城市主干道的车速
    'T': 1.4,
    's0': 1.5,
    'a': 1.5,
    'b': 2 
}

########################## 边界条件设置 ##########################

# 生成车辆的规则，各进口道各转向的车辆在每条进口道上的流量。单位：pcu/hour
veh_gen_rule_table = { 
    # 3车道的情况
    'Nl': [800 * 0.5, 0        , 0        ], 
    'Nt': [0        , 800 * 0.8, 0        ], 
    'Nr': [0        , 0        , 800 * 0.5], 
    'Sl': [800 * 0.5, 0,         0        ], 
    'St': [0        , 800 * 0.8, 0        ], 
    'Sr': [0        , 0        , 800 * 0.5], 
    'El': [800 * 0.5, 0        , 0        ], 
    'Et': [0        , 800 * 0.8, 0        ], 
    'Er': [0        , 0        , 800 * 0.5], 
    'Wl': [800 * 0.5, 0        , 0        ], 
    'Wt': [0        , 800 * 0.8, 0        ], 
    'Wr': [0        , 0        , 800 * 0.5]

    # 'Nl': [0        , 0        , 0        ],
    # 'Nt': [0        , 0        , 0        ],
    # 'Nr': [0        , 0        , 0        ],
    # 'Sl': [0        , 0        , 0        ],
    # 'St': [0        , 0        , 0        ],
    # 'Sr': [0        , 0        , 0        ],
    # 'El': [1200     , 0        , 0        ], 
    # 'Et': [0        , 1600     , 0        ], 
    # 'Er': [0        , 0        , 1000     ], 
    # 'Wl': [0        , 0        , 0        ],
    # 'Wt': [0        , 0        , 0        ], 
    # 'Wr': [0        , 0        , 0        ],
}
# 车辆生成时的初始位置
gen_init_x = - arm_len
# 车辆生成时的初始速度（在路段行驶的速度）
gen_init_v = cf_param['v0']
# 一个车道上生成连续两辆车的最短空距、时距，以防止车辆相撞。单位：米、秒
min_gen_hs = veh_param['veh_len'] + cf_param['s0'] + gen_init_v * cf_param['T']
min_gen_ht = min_gen_hs / gen_init_v
for key, value in veh_gen_rule_table.items():
    for i in range(len(value)):
        value[i] = value[i] * veh_dt / (3600 - min_gen_ht * value[i])
# veh_gen_rule_table 现在的单位是生成车的概率 / timestep
        
########################## 交叉口控制方案设置 ##########################
inter_control_mode = 'traffic light' # 'traffic light', 'Dresner'
