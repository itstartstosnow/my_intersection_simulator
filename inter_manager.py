import logging
from lib.settings import inter_control_mode

class BaseInterManager:
    def __init__(self):
        self.timestep = 0
    def update(self):
        self.timestep += 1
    def receive_V2I(self, sender, message):
        pass

class TrafficLightManager(BaseInterManager):
    def __init__(self):
        super().__init__()
        self.timestep = 0
        self.current_phase = 0
        self.current_elapsed_time = 0
        self.phase = [
            [200, 'Nl', 'Sl'],
            [250, 'Nt', 'St', 'Nr', 'Sr'],
            [200, 'El', 'Wl'],
            [250, 'Et', 'Wt', 'Er', 'Wr']
        ]

    def update(self):
        super().update()
        self.update_phase()
    
    def update_phase(self):
        self.current_elapsed_time += 1
        message = {}
        if self.current_elapsed_time == self.phase[self.current_phase][0]:
            # 这个相位结束了，换下一个相位
            self.current_elapsed_time = 0
            self.current_phase = (self.current_phase + 1) % len(self.phase)
        if self.current_elapsed_time >= self.phase[self.current_phase][0] - 30:
            # 到黄灯时间了
            for ap_arm_dir in ['Nl', 'Nt', 'Nr', 'Sl', 'St', 'Sr', 'El', 'Et', 'Er', 'Wl', 'Wt', 'Wr']:
                if ap_arm_dir in self.phase[self.current_phase]:
                    message[ap_arm_dir] = 'Y'
                else: 
                    message[ap_arm_dir] = 'R'
            ComSystem.I_broadcast(message)
        else:
            for ap_arm_dir in ['Nl', 'Nt', 'Nr', 'Sl', 'St', 'Sr', 'El', 'Et', 'Er', 'Wl', 'Wt', 'Wr']:
                if ap_arm_dir in self.phase[self.current_phase]:
                    message[ap_arm_dir] = 'G'
                else: 
                    message[ap_arm_dir] = 'R'
            ComSystem.I_broadcast(message)
        
    def receive_V2I(self, sender, message):
        return 

class DresnerManager(BaseInterManager):
    def __init__(self):
        super().__init__()
        self.timestep = 0
        self.grid = None


    def update(self):
        BaseInterManager.update()
        # Todo：删除一些过去的时刻
    def receive_V2I(self, sender, message):
        if message['type'] == 'request':
            reservation = check_request()
            message = {'type': None}
            if reservation:
                message['type'] = 'confirm'
                ComSystem.I2V(sender, message)
            else: 
                message['type'] = 'reject'
                ComSystem.I2V(sender, reservation)
        elif message['type'] == 'change-request':
            pass
        elif message['type'] == 'cancel':
            # process cancel with P
            ComSystem.I2V(sender, {'type': 'acknowledge'})
        elif message['type'] == 'done':
            # record any statistics supplied in message
            # process cancel with P
            ComSystem.I2V(sender, {'type': 'acknowledge'})
    def check_request(self): 
        pass
        # confirm时返回reservation，当reject时返回None
        

# 根据设置选择某个实现
if inter_control_mode == 'traffic light':
    inter_manager = TrafficLightManager()
elif inter_control_mode == 'Dresner':
    inter_manager = DresnerManager()

# 这不是上策，但是先这样吧
import simulator

class ComSystem:
    @staticmethod
    def V2V(receiver, sender, message):
        receiver.receive_V2V(sender, message)

    @staticmethod   
    def V2I(sender, message):
        inter_manager.receive_V2I(sender, message)

    @staticmethod
    def I2V(receiver, message):
        receiver.receive_I2V(message)

    @staticmethod
    def I_broadcast(message):
        logging.debug(str(message))
        for group, vehs in simulator.Simulator.getInstance().all_veh.items():
            for veh in vehs:
                veh.receive_broadcast(message)
        
