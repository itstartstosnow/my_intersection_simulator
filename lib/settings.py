########################## 全局步长设置 ##########################
veh_dt = 0.1
disp_dt = 0.04
simu_t = 600 # simulation time = 10 min
time_wrap = 4

########################## 场景参数设置 ##########################
lane_width = 3.5
turn_radius = 6 # 美国城市街道设计指南要求一般城市道路交叉口转角半径采用3~4.5m
arm_len = 100
NS_lane_count = 1
EW_lane_count = 1
arm_v_lim = 16.66    # 60 km/h
inter_v_lim = 11.11  # 交叉口区域的限速，Human/Dresner/Xu都会用到
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
    'b': 3 
}

########################## 边界条件设置 ##########################

# 生成车辆的规则，各进口道各转向的车辆在每条进口道上的流量。单位：pcu/hour
veh_gen_rule_table = { 
    # 3车道的情况
    'Nl': [0    , 0    , 0    ],
    'Nt': [0    , 0    , 0    ],
    'Nr': [0    , 0    , 0    ],
    'Sl': [0    , 0    , 0    ],
    'St': [0    , 0    , 0    ],
    'Sr': [0    , 0    , 0    ],
    'El': [1800 , 0    , 0    ], 
    'Et': [0    , 1800 , 0    ], 
    'Er': [0    , 0    , 1800 ], 
    'Wl': [0    , 0    , 0    ],
    'Wt': [0    , 0    , 0    ], 
    'Wr': [0    , 0    , 0    ],
}
# 车辆生成时的初始速度（在路段行驶的速度）
gen_init_v = cf_param['v0']
# 一个车道上生成连续两辆车的最短空距、时距，单位：米、秒
min_gen_hs = veh_param['veh_len'] + cf_param['s0'] + gen_init_v**2 / 2 / veh_param['max_dec']
min_gen_ht = min_gen_hs / gen_init_v
        
########################## 交叉口控制方案设置 ##########################
inter_control_mode = 'Dresner' # 'traffic light', 'Dresner', 'Xu'

########################## 信号灯的仿真参数  ##########################
phase = [
            # [200, 'Nl', 'Nt', 'Nr'], 
            # [200, 'Sl', 'St', 'Sr'], 
            # [200, 'El', 'Et', 'Er'], 
            # [200, 'Wl', 'Wt', 'Wr']
            [100, 'Nl', 'Nt', 'Nr'], 
            [190, 'Sl', 'St', 'Sr'], 
            [190, 'El', 'Et', 'Er'], 
            [380, 'Wl', 'Wt', 'Wr']
            # [150, 'Nl', 'Sl', 'Nr', 'Sr', 'Er', 'Wr'],
            # [220, 'Nt', 'St', 'Nr', 'Sr', 'Er', 'Wr'],
            # [150, 'El', 'Wl', 'Nr', 'Sr', 'Er', 'Wr'],
            # [220, 'Et', 'Wt', 'Nr', 'Sr', 'Er', 'Wr']
        ]
yellow_time = 1.5

########################## Dresner 的仿真参数  ##########################
inter_v_lim_min = 4  # Dresner 方案中通过交叉口的最慢速度

##########################   Xu 的仿真参数   ##########################
desired_cf_distance = 25 # 单车道取 25，三车道取 39
virtual_lead_v = inter_v_lim
kp = 0.15
kv = 0.7

conflict_movements = {
    # 对于单车道的情况，同一进口道和出口道的都具有分流和合流冲突
    # ['Nl', 'Nt', 'Nr', 'Sl', 'St', 'Sr', 'Wl', 'Wt', 'Wr', 'El', 'Et', 'Er']
    'Nl': ['Nl', 'Nt', 'Nr', 'St', 'Sr', 'Wl', 'Wt', 'El', 'Et'],
    'Nt': ['Nl', 'Nt', 'Nr', 'Sl', 'Wl', 'Wt', 'Wr', 'El', 'Et'],
    'Nr': ['Nl', 'Nt', 'Nr', 'Sl', 'Et'],
    'Sl': ['Nt', 'Nr', 'Sl', 'St', 'Sr', 'Wl', 'Wt', 'El', 'Et'],
    'St': ['Nl', 'Sl', 'St', 'Sr', 'Wl', 'Wt', 'El', 'Et', 'Er'],
    'Sr': ['Nl', 'Sl', 'St', 'Sr', 'Wt'],
    'Wl': ['Nl', 'Nt', 'Sl', 'St', 'Wl', 'Wt', 'Wr', 'Et', 'Er'], 
    'Wt': ['Nl', 'Nt', 'Sl', 'St', 'Sr', 'Wl', 'Wt', 'Wr', 'El'], 
    'Wr': ['Nt', 'Wl', 'Wt', 'Wr', 'El'], 
    'El': ['Nl', 'Nt', 'Sl', 'St', 'Wt', 'Wr', 'El', 'Et', 'Er'], 
    'Et': ['Nl', 'Nt', 'Nr', 'Sl', 'St', 'Wl', 'El', 'Et', 'Er'], 
    'Er': ['St', 'Wl', 'El', 'Et', 'Er']
}
# conflict_movements = {
#     # 对于三车道，不存在分流和合流冲突了
#     # ['Nl', 'Nt', 'Nr', 'Wl', 'Wt', 'Wr', 'Sl', 'St', 'Sr', 'El', 'Et', 'Er']
#     'Nl': ['Nl', 'Wl', 'St', 'El', 'Et'],
#     'Nt': ['Nt', 'Wl', 'Wt', 'Sl', 'Et'], 
#     'Nr': ['Nr'], 
#     'Sl': ['Nt', 'Wl', 'Wt', 'Sl', 'El'], 
#     'St': ['Nl', 'Wt', 'St', 'El', 'Et'], 
#     'Sr': ['Sr'], 
#     'Wl': ['Nl', 'Nt', 'Wl', 'Sl', 'Et'], 
#     'Wt': ['Nt', 'Wt', 'Sl', 'St', 'El'], 
#     'Wr': ['Wr'], 
#     'El': ['Nl', 'Wt', 'Sl', 'St', 'El'], 
#     'Et': ['Nl', 'Nt', 'Wl', 'St', 'Et'], 
#     'Er': ['Er']
# }
