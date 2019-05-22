import copy
import logging

from vehicle import Vehicle
from lib.settings import arm_len, veh_dt, veh_param, cf_param, NS_lane_count, EW_lane_count, veh_gen_rule_table, min_gen_hs, gen_init_v, gen_init_x

import numpy as np

class Simulator:
    _instance = None

    @staticmethod 
    def getInstance():
        if Simulator._instance == None:
            Simulator()
        return Simulator._instance

    def __init__(self):
        if Simulator._instance != None:
            raise Exception("This class is a singleton, but more than one objects are created.")
        else:
            Simulator._instance = self

        self.timestep = 0

        # 生成车辆的计数，用于车辆 ID 的分配
        self.gen_veh_count = 0  
        # 每条车道未放进仿真区域的车辆队列，参照 Meng2018Analysis 文章
        self.point_queue_table = self.init_point_queue_table()
        # 仿真区域的车辆
        self.all_veh = {
            'Nap': [],
            'Sap': [],
            'Eap': [],
            'Wap': [],
            'Nex': [],
            'Sex': [],
            'Eex': [],
            'Wex': [],
            'ju': []
        }

    def update(self):
        self.timestep += 1
        to_switch_group = self.all_update_position()
        self.update_group(to_switch_group)
        self.gen_new_veh()
        self.remove_out_veh()
        self.update_all_control()

    def all_update_position(self):
        '''对于在 all_veh 中的车辆，更新位置，顺便记录分组有变化的车辆'''
        to_switch_group = []
        for group, vehs in self.all_veh.items():
            for veh in vehs:
                switch_group = veh.update_position(veh_dt)
                if switch_group:
                    to_switch_group.append([veh, group])
        return to_switch_group
    
    def update_group(self, to_switch_group):
        '''更新车辆所在分组，并在车道内按照位置排序'''
        for veh, old_group in to_switch_group:
            if veh.zone == 'ju':
                new_group = 'ju'
            elif veh.zone == 'ex':
                new_group = str(veh.track.ex_arm) + 'ex'
            self.all_veh[new_group].append(veh)
            self.all_veh[old_group].remove(veh)

        for group, vehs in self.all_veh.items():
            vehs.sort(key=lambda veh: veh.inst_x) # 按照x从小到大排序
            # logging.debug("group %s: veh %s" % (group, [veh._id for veh in vehs])) 

    def remove_out_veh(self):
        '''删去跑出仿真区域的车辆'''
        to_delete = []
        for group, vehs in self.all_veh.items():
            if group[-2:] == 'ex':
                for veh in vehs:
                    if veh.inst_x >= arm_len + veh.veh_len_back:
                        to_delete.append([group, veh])
        for group, veh in to_delete:
            self.all_veh[group].remove(veh)

    def init_point_queue_table(self):
        point_queue_table = {}
        for i in range(NS_lane_count):
            point_queue_table['N' + str(i)] = [] # 列表中的元素是将要生成的各车辆的转向
            point_queue_table['S' + str(i)] = []
        for i in range(EW_lane_count):
            point_queue_table['E' + str(i)] = []
            point_queue_table['W' + str(i)] = []
        return point_queue_table       

    def gen_new_veh(self): 
        '''按照概率在 point_queue 生成新的车辆，如果可行，将一辆车放进仿真区域'''
        for ap_arm in 'NSEW': # 各个进口道路
            for turn_dir in 'lrt': # 各个方向
                probs = veh_gen_rule_table[ap_arm + turn_dir]
                for (lane, prob) in enumerate(probs): # 第 lane 个车道 
                    if np.random.rand() < prob:
                        self.point_queue_table[ap_arm + str(lane)].insert(0, turn_dir)
        for ap_arm_lane, queue in self.point_queue_table.items():
            ap_arm = ap_arm_lane[0]
            lane = int(ap_arm_lane[1])
            latest_veh = None 
            for some_veh in self.all_veh[ap_arm + 'ap']:
                if some_veh.inst_lane == lane:
                    latest_veh = some_veh
                    break
            if not latest_veh or (latest_veh.inst_x - gen_init_x) > min_gen_hs:
                if len(queue) > 0: 
                    new_veh = self.make_veh(ap_arm, lane, queue.pop())
                    self.all_veh[ap_arm + 'ap'].insert(0, new_veh)
                    # logging.debug('point_queue_table[%s] = %s' % (ap_arm_lane, str(queue)))
                    
    def make_veh(self, ap_arm, ap_lane, turn_dir):
        '''创建一个车辆对象并返回'''
        new_veh_param = copy.deepcopy(veh_param)
        new_veh_param['ap_arm'] = ap_arm
        new_veh_param['ap_lane'] = ap_lane
        new_veh_param['turn_dir'] = turn_dir
        new_veh = Vehicle(self.gen_veh_count, new_veh_param, cf_param, gen_init_v, self.timestep)
        self.gen_veh_count += 1
        return new_veh

    def update_all_control(self):
        '''所有车辆自主更新控车状态'''
        for group, vehs in self.all_veh.items():
            for (i, veh) in enumerate(vehs):
                lead_veh = None
                if group != 'ju': # 进出口道
                    for j in range(i+1, len(vehs)):
                        if vehs[j].inst_lane == veh.inst_lane:
                            lead_veh = vehs[j]
                            break
                else: # 交叉口，这里本没有车道概念，但是为了防止轨迹一致的前后两车相撞，还是认为它们在同一车道上
                    for j in range(i+1, len(vehs)):
                        if vehs[j].track.ap_arm == veh.track.ap_arm and vehs[j].track.ap_lane == veh.track.ap_lane \
                            and vehs[j].track.turn_dir == veh.track.turn_dir and vehs[j].track.ex_lane == veh.track.ex_lane:
                            lead_veh = vehs[j]
                            break
                veh.update_control(lead_veh)



    