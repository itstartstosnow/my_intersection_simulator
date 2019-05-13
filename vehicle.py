import math
import logging

from lib.settings import arm_len, inter_v_lim, arm_v_lim, inter_control_mode, veh_dt
from map import Track
from inter_manager import ComSystem

class BaseVehicle:
    '''
    units: meter, second
    x is defined as the position of Front bumper
    '''
    def __init__(self, id, veh_param, cf_param, init_v, timestep):
        # static
        self._id = id
        self.veh_wid = veh_param['veh_wid']
        self.veh_len = veh_param['veh_len']
        self.veh_len_front = veh_param['veh_len_front']
        self.veh_len_back = self.veh_len - self.veh_len_front
        self.max_v = veh_param['max_v']
        self.max_acc = veh_param['max_acc']
        self.max_dec = veh_param['max_dec']
        self.track = Track(veh_param['ap_arm'], veh_param['ap_lane'], veh_param['turn_dir'])

        # dynamic
        self.timestep = timestep
        self.inst_a = 0
        self.inst_v = init_v
        self.zone = 'ap'                       # 'ap' = approach lane, 'ju' = junction area, 'ex' = exit lane
        self.inst_lane = veh_param['ap_lane']  # 当 zone == 'ap' or 'ex'，现在的车道
        self.inst_x = -arm_len                 # 当 zone == 'ap'，是 (- 到停车线的距离)；zone == 'ju'，是在交叉口内沿轨迹行驶的距离；zone == 'ex'，是沿出口道行驶的距离

        # 设置跟车参数
        cf_param['v0'] = min(self.max_v, cf_param['v0'])
        self.cf_model = CFModel(cf_param=cf_param)

        # self.track.confirm_ex_lane(0)

    def __eq__(self, vehicle):  
        # 运算符重载，经测试好像是能传给后代的
        return self._id == vehicle._id

    def acc_with_lead_veh(self, lead_veh):
        '''仅考虑跟车时，执行的加速度'''
        if not lead_veh:
            # 没有前车，就假设前车无穷远
            return self.cf_model.acc_from_model(self.inst_v, 1e3, self.cf_model.v0)
        else: 
            s = lead_veh.inst_x - self.inst_x - lead_veh.veh_len
            v_l = lead_veh.inst_v
            return self.cf_model.acc_from_model(self.inst_v, s, v_l)

    def update_control(self, lead_veh):
        '''等着在子类里被重写吧兄弟'''
        # 仅考虑前车
        self.inst_a = self.acc_with_lead_veh(lead_veh)
        # 根据车辆性能，限制一下最大最小
        self.inst_a = min(max(self.inst_a, - self.max_dec), self.max_acc)

    def update_position(self, dt):
        '''相当于做积分，更新位置和速度. 返回：zone是否发生了更改'''
        self.timestep += 1

        self.inst_x += self.inst_a * (dt ** 2) / 2 + self.inst_v * dt
        self.inst_v += self.inst_a * dt
        self.inst_v = min(self.inst_v, self.max_v)
        self.inst_v = max(self.inst_v, 0)

        if self.zone == 'ap' and self.inst_x >= 0:
            self.zone = 'ju'
            self.inst_lane = -1
            return True
        elif self.zone == 'ju' and self.inst_x >= self.track.ju_shape_end_x[-1]: 
            self.zone = 'ex'
            self.inst_x -= self.track.ju_shape_end_x[-1]
            self.inst_lane = self.track.ex_lane
            return True
        
        logging.debug("time %d, veh %d, %s, lane %d, x = %.1f, v = %.1f" % (self.timestep, self._id, self.zone, self.inst_lane, self.inst_x, self.inst_v))
        return False

    def receive_broadcast(self, message):
        pass
    
    def receive_I2V(self, message):
        pass

class HumanDrivenVehicle(BaseVehicle):
    '''人工驾驶的车，只相应信号灯'''
    def __init__(self, id, veh_param, cf_param, init_v, timestep):
        super().__init__(id, veh_param, cf_param, init_v, timestep)
        
        # 控制信息
        self.track.confirm_ex_lane(0)
        self.traffic_light = None # control_order

        # 跟车参数的备份 
        self.cf_v0_backup = None
        self.cf_T_backup = None

    def update_control(self, lead_veh):
        # 考虑前车
        self.inst_a = super().acc_with_lead_veh(lead_veh)
        # 在进口道遇到红灯或者黄灯时，不能越过停车线
        if self.zone == 'ap' and self.traffic_light != 'G':
            self.inst_a = min(self.inst_a, self.cf_model.acc_from_model(self.inst_v, - self.inst_x - self.veh_len_front, 0))
        # 限制最大最小值
        self.inst_a = min(max(self.inst_a, - self.max_dec), self.max_acc)

    def update_position(self, dt):
        switch_group = super().update_position(dt)
        if self.zone == 'ap' and self.inst_x > -50 and not self.cf_v0_backup:
            # 当距离交叉口较近时，期望速度改为交叉口限速，车头时距改小
            self.cf_v0_backup = self.cf_model.v0
            self.cf_T_backup = self.cf_model.T
            self.cf_model.v0 = min(self.cf_model.v0, inter_v_lim)
            self.cf_model.T = min(self.cf_model.T, 1)
        elif self.zone == 'ex' and switch_group: 
            # 刚刚从交叉口区域变到出口道，改回来跟车参数
            self.cf_model.v0 = self.cf_v0_backup
            self.cf_model.T = self.cf_T_backup
        return switch_group

    def receive_broadcast(self, message):
        if self.zone == 'ap':
            self.traffic_light = message[self.track.ap_arm + self.track.turn_dir]
            logging.debug('self.traffic_light =' + str(self.traffic_light))

    def receive_I2V(self, message):
        '''不听不听王八念经'''
        return

class DresnerVehicle(BaseVehicle):
    '''对应 Dresner 文中的自动驾驶车，响应 DresnerManager'''
    def __init__(self, id, veh_param, cf_param, init_v, timestep):
        super().__init__(id, veh_param, cf_param, init_v, timestep)
        # 控制信息
        self.reservation = None
        self.timeout = 0         # Unit: s
        # 文中的 optimistic 和 pessimistic
        self.optimism = True
        self.ap_acc_profile = None

    def plan_arr(self):
        '''按照 arr_v 最大、arr_t 最大计划到达时间和速度。因为只有一个车道的头车才能计划这个，因此只要获得预约，计划肯定能被执行'''
        if self.inst_v < inter_v_lim: 
            acc_distance = (inter_v_lim**2 - self.inst_v**2) / 2 / self.max_acc # 加速到 v_lim 所需要的距离
            if acc_distance >= (-self.inst_x):
                # 到停车线还加速不到 v_lim，就全程加速
                arr_v = math.sqrt(self.inst_v**2 + 2*self.max_acc*(-self.inst_x))
                t1 = (arr_v - self.inst_v) / self.max_acc
                arr_t = self.timestep + t1 / veh_dt
                self.ap_acc_profile = [[self.timestep, self.max_acc]]
            else: 
                # 不到停车线就加速够了，暂时先加速-匀速吧，加速-减速太难算了
                arr_v = inter_v_lim
                t1 = (inter_v_lim - self.inst_v) / self.max_acc
                t2 = ((-self.inst_x) - acc_distance) / inter_v_lim
                arr_t = self.timestep + (t1+t2) / veh_dt
                self.ap_acc_profile = [
                    [self.timestep, self.max_acc],
                    [self.timestep + t1/veh_dt, 0]
                ]
        else:
            # 现在速度超过了v_lim，匀速-减速 (不该出现减速减不下来的情况)
            dec_distance = (inter_v_lim**2 - self.inst_v**2) / 2 / -(self.max_dec)
            if dec_distance > (-self.inst_x):
                print('Error: veh %d is unable to brake at stop bar' % self._id)
                arr_v = self.inst_v
                arr_t = self.timestep + ((-self.inst_x) / self.inst_v) / veh_dt
                self.ap_acc_profile = [[self.timestep, 0]]
            else:
                arr_v = inter_v_lim
                t2 = (self.inst_v - inter_v_lim) / self.max_dec
                t1 = ((-self.inst_x) - dec_distance) / self.inst_v
                arr_t = self.timestep + (t1+t2) / veh_dt
                self.ap_acc_profile = [
                    [self.timestep, 0],
                    [self.timestep + t1/veh_dt, -self.max_dec]
                ]
        return [arr_t, arr_v]
    
    def update_control(self, lead_veh):
        if self.zone == 'ap':
            if not lead_veh and not self.reservation:
                # 已经没有前车了，就使劲预约
                [arr_t, arr_v] = self.plan_arr()
                logging.debug("veh %d, arr_t = %d, arr_v = %d, ap_acc_profile = %s" % (self._id, arr_t, arr_v, self.ap_acc_profile))
                ComSystem.V2I(self, {
                    'type': 'request',
                    'veh_id': self._id, 
                    'arr_t': arr_t, 
                    'arr_v': arr_v, 
                    'arr_arm': self.track.ap_arm,
                    'arr_lane': self.track.ap_lane, 
                    'turn_dir': self.track.turn_dir, 
                    'veh_len': self.veh_len, 
                    'veh_wid': self.veh_wid, 
                    'veh_len_front': self.veh_len_front,
                    'max_acc': self.max_acc,
                    'max_dec': self.max_dec
                })
            if self.reservation:
                # 预约成功，按照之前算的 plan 执行加速
                for t, a in self.ap_acc_profile:
                    if self.timestep >= t:
                        self.inst_a = a
                logging.debug("veh %d, according to ap_acc_profile, inst_a = %f" % (self._id, self.inst_a))
            else:
                # 不成功，prepare to stop at stop bar & follow leading vehicle
                self.inst_a = min(self.acc_with_lead_veh(lead_veh), self.cf_model.acc_from_model(self.inst_v, - self.inst_x - self.veh_len_front, 0))
        elif self.zone == 'ju':
            # 按照 reservation 的 acc 要求跑
            for t, a in self.reservation['acc']:
                if self.timestep >= t:
                    self.inst_a = a
        else:
            # exit lane, perform normal car following
            super().update_control(lead_veh)

    def update_position(self, dt):
        switch_group = super().update_position(dt)
        if switch_group and self.zone == 'ex':
            ComSystem.V2I(self, {
                'type': 'done',
                'veh_id': self._id, 
                'res_id': self.reservation['res_id']
            })
        return switch_group

    def receive_broadcast(self, message):
        '''暂时不听'''
        pass

    def receive_I2V(self, message):
        if message['type'] == 'acknowledge':
            if message['res_id'] != self.reservation['res_id']:
                print('Error: ack message with [\'res_id\'] = %d is sent to veh %d' % (message['res_id'], self._id))
        elif message['type'] == 'confirm':
            self.reservation = message['reservation']
            self.track.confirm_ex_lane(self.reservation['ex_lane'])
        elif message['type'] == 'reject':
            self.timeout = message['timeout']

# 根据设置选择某个实现
if inter_control_mode == 'traffic light':
    Vehicle = HumanDrivenVehicle
elif inter_control_mode == 'Dresner':
    Vehicle = DresnerVehicle

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

