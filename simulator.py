import copy
import logging

from vehicle import Vehicle
from lib.settings import arm_len, veh_dt, veh_param, cf_param, veh_gen_rule_table, min_gen_hs, gen_init_v, gen_init_x
from inter_manager import InterManager

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

        self.gen_veh_count = 0  # generated vehicle count
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

        InterManager.getInstance().sync_time(self.timestep)

    def all_update_position(self):
        '''更新所有车辆位置，顺便记录分组有变化的车辆'''
        to_switch_group = []
        for group, vehs in self.all_veh.items():
            for veh in vehs:
                switch_group = veh.update_position(veh_dt, self.timestep)
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

    def remove_out_veh(self):
        '''删去跑出仿真区域的车辆'''
        to_delete = []
        for group, vehs in self.all_veh.items():
            if group[-2:] == 'ex':
                for veh in vehs:
                    if veh.inst_x > arm_len + veh.veh_len:
                        to_delete.append([group, veh])
        for group, veh in to_delete:
            self.all_veh[group].remove(veh)

    def gen_new_veh(self): 
        '''按照概率在进口道起始位置生成新的车辆'''
        for ap_arm in 'NSEW':
            for turn_dir in 'lrt':
                probs = veh_gen_rule_table[ap_arm + turn_dir]
                for (i, prob) in enumerate(probs): # 第 i 个车道
                    if prob == 0: 
                        continue
                    latest_veh = None 
                    for some_veh in self.all_veh[ap_arm + 'ap']:
                        if some_veh.inst_lane == i:
                            latest_veh = some_veh
                            break
                    if not latest_veh or (latest_veh.inst_x - gen_init_x) > min_gen_hs: 
                        if np.random.rand() < prob:
                            new_veh = self.make_veh(ap_arm, i, turn_dir)
                            self.all_veh[str(ap_arm) + 'ap'].insert(0, new_veh)
                    
    def make_veh(self, ap_arm, ap_lane, turn_dir):
        '''创建一个车辆对象并返回'''
        new_veh_param = copy.deepcopy(veh_param)
        new_veh_param['ap_arm'] = ap_arm
        new_veh_param['ap_lane'] = ap_lane
        new_veh_param['turn_dir'] = turn_dir
        new_veh = Vehicle(self.gen_veh_count, new_veh_param, cf_param, gen_init_v)
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



    