import math
import logging

from lib.settings import arm_len
from map import Track
from inter_manager import ComSystem

class Vehicle:
    '''
    units: meter, second
    x is defined as the position of Front bumper
    '''
    def __init__(self, id, veh_param, cf_param, init_v):
        # static
        self._id = id
        self.veh_wid = veh_param['veh_wid']
        self.veh_len = veh_param['veh_len']
        self.max_v = veh_param['max_v']
        self.max_acc = veh_param['max_acc']
        self.max_dec = veh_param['max_dec']
        self.track = Track(veh_param['ap_arm'], veh_param['ap_lane'], veh_param['turn_dir'])

        # dynamic
        self.inst_a = 0
        self.inst_v = init_v
        self.zone = 'ap'                       # 'ap' = approach lane, 'ju' = junction area, 'ex' = exit lane
        self.inst_lane = veh_param['ap_lane']  # 当 zone == 'ap' or 'ex'，现在的车道
        self.inst_x = -arm_len                 # 当 zone == 'ap'，是 (- 到停车线的距离)；zone == 'ju'，是在交叉口内沿轨迹行驶的距离；zone == 'ex'，是沿出口道行驶的距离

        # 设置跟车参数
        cf_param['v0'] = min(self.max_v, cf_param['v0'])
        self.cf_model = CFModel(cf_param=cf_param)

        # 控制信息
        self.control_order = None
        self.track.confirm_ex_lane(0)

    def __eq__(self, vehicle):  # 运算符重载
        return self._id == vehicle._id

    def update_control(self, lead_veh):
        if self.zone == 'ap':
            if not self.control_order or self.control_order['order'] == 'G':
                if not lead_veh:
                    # 没有前车，就假设前车无穷远
                    self.inst_a = self.cf_model.acc_from_model(self.inst_v, 1e3, self.cf_model.v0)
                else: 
                    s = lead_veh.inst_x - self.inst_x - lead_veh.veh_len
                    v_l = lead_veh.inst_v
                    self.inst_a = self.cf_model.acc_from_model(self.inst_v, s, v_l)
            else:
                if not lead_veh:
                    # 认为停车线位置是前车，且速度为 0
                    self.inst_a = self.cf_model.acc_from_model(self.inst_v, - self.inst_x, 0) 
                else:
                    # 有前车
                    s = lead_veh.inst_x - self.inst_x - lead_veh.veh_len
                    v_l = lead_veh.inst_v
                    self.inst_a = self.cf_model.acc_from_model(self.inst_v, s, v_l)
        elif self.zone == 'ex':
            if not lead_veh:
                self.inst_a = self.cf_model.acc_from_model(self.inst_v, 1e3, self.cf_model.v0)
            else: 
                s = lead_veh.inst_x - self.inst_x - lead_veh.veh_len
                v_l = lead_veh.inst_v
                self.inst_a = self.cf_model.acc_from_model(self.inst_v, s, v_l)
        elif self.zone == 'ju':
            self.inst_a = (self.cf_model.v0 - self.inst_v) / 5
            
        # 根据车辆性能，限制一下最大最小
        self.inst_a = min(max(self.inst_a, - self.max_dec), self.max_acc)

    def receive_broadcast(self, message):
        if self.zone == 'ap' and message['mode'] == 'traffic light':
            self.control_order = {
                'mode': 'traffic light',
                'order': message[self.track.ap_arm + self.track.turn_dir]
            }
            logging.debug('self.control_order =' + str(self.control_order))

    def receive_I2V(self, message):
        pass

    def update_position(self, dt, timestep):
        '''相当于做积分，更新位置和速度. 返回：zone是否发生了更改'''
        self.inst_v += self.inst_a * dt
        self.inst_v = min(self.inst_v, self.max_v)
        self.inst_v = max(self.inst_v, 0)
        self.inst_x += self.inst_a * (dt ** 2) / 2 + self.inst_v * dt

        if self.zone == 'ap' and self.inst_x >= 0:
            self.zone = 'ju'
            self.inst_lane = -1
            return True
        elif self.zone == 'ju' and self.inst_x >= self.track.ju_shape_end_x[-1]: 
            self.zone = 'ex'
            self.inst_x -= self.track.ju_shape_end_x[-1]
            self.inst_lane = self.track.ex_lane
            return True
        
        logging.debug("Timestep: %d, veh %d, %s, %d lane, x = %.1f" % (timestep, self._id, self.zone, self.inst_lane, self.inst_x))
        return False


class CFModel:
    '''Car-following model, here we use IDM model'''
    def __init__(self, cf_param):
        self.v0 = cf_param['v0']    # desired speed
        self.T = cf_param['T']      # desired time headway
        self.s0 = cf_param['s0']    # minimum gap when stopped
        self.a = cf_param['a']      # acceleration rate
        self.b = cf_param['b']      # deceleration rate
        self.delta = 4

    def acc_from_model(self, v, s, v_l):
        '''
        v       speed
        s       gap with front vehicle
        v_l     speed of the leading vehicle
        '''
        s_star = self.s0 + max(0, v * self.T + v * (v - v_l) / 2 / math.sqrt(self.a * self.b))
        if v < self.v0:
            acc_free = self.a * (1 - (v / self.v0)**self.delta)
        else:
            acc_free = self.a * (1 - v / self.v0) # 如果 v > v0 就按照 1 次方
        dec = - self.a * (s_star / max(s, self.s0))**2 # 这里处理一下 s < s0 的情况，按照 s0 算
        acc = acc_free + dec
        return acc

