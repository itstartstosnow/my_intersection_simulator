import logging
from lib.settings import inter_control_mode

class BaseInterManager:
    def update(self):
        pass
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
        self.timestep += 1
        self.update_phase()
    
    def update_phase(self):
        self.current_elapsed_time += 1
        message = {'mode': 'traffic light'}
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

# 根据设置选择某个实现
if inter_control_mode == 'traffic light':
    inter_manager = TrafficLightManager()

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
        
