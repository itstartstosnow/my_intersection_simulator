import math
import logging

from lib.settings import inter_control_mode, lane_width, turn_radius, arm_len, NS_lane_count, EW_lane_count, veh_dt, inter_v_lim, inter_v_lim_min, min_gen_ht, conflict_movements, virtual_lead_v, desired_cf_distance
from map import Map, Track

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

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
        self.current_phase = 0
        self.current_elapsed_time = 0
        self.phase = [
            [150, 'Nl', 'Sl', 'Nr', 'Sr'],
            [220, 'Nt', 'St', 'Nr', 'Sr'],
            [150, 'El', 'Wl', 'Nr', 'Sr'],
            [220, 'Et', 'Wt', 'Nr', 'Sr']
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
        self.res_grid = DresnerResGrid(0.5) # 写到设置里？
        self.ex_lane_table = self.gen_ex_lane_table()
        self.res_registery = {}

    def update(self):
        super().update()
        self.res_grid.dispose_passed_time(self.timestep)

    def receive_V2I(self, sender, message):
        if message['type'] == 'request':
            reservation = self.check_request(message)
            if reservation:
                reply_message = {
                    'type': 'confirm',
                    'reservation': reservation
                }
                self.res_registery[message['veh_id']] = reservation['res_id']
                ComSystem.I2V(sender, reply_message)
            else: 
                reply_message = {
                    'type': 'reject',
                    'timeout': 1
                }
                ComSystem.I2V(sender, reply_message)
        elif message['type'] == 'change-request':
            pass
        elif message['type'] == 'cancel':
            # process cancel with P
            pass
        elif message['type'] == 'done':
            # record any statistics supplied in message
            # process cancel with P
            self.res_registery.pop(message['veh_id']) # dict.pop(key)返回value并删除
            ComSystem.I2V(sender, {
                'type': 'acknowledge',
                'res_id': message['res_id']
            })

    def gen_ex_lane_table(self):
        table = {}
        table['Nl'] = list(range(EW_lane_count))
        table['Sl'] = table['Nl']
        table['El'] = list(range(NS_lane_count))
        table['Wl'] = table['El']
        table['Nr'] = list(range(EW_lane_count - 1, -1, -1))
        table['Sr'] = table['Nr']
        table['Er'] = list(range(NS_lane_count - 1, -1, -1))
        table['Wr'] = table['Sr']
        for i in range(NS_lane_count):
            ti_list = [i]
            left_finished, right_finished = False, False
            for j in range(1, EW_lane_count):
                if not left_finished:
                    if i - j >= 0:
                        ti_list.append(i - j)
                    else:
                        left_finished = True
                if not right_finished:
                    if i + j < EW_lane_count:
                        ti_list.append(i + j)
                    else:
                        right_finished = True
                if left_finished and right_finished:
                    break
            table['Nt' + str(i)] = ti_list
            table['St' + str(i)] = ti_list
        for i in range(EW_lane_count):
            ti_list = [i]
            left_finished, right_finished = False, False
            for j in range(1, NS_lane_count):
                if not left_finished:
                    if i - j >= 0:
                        ti_list.append(i - j)
                    else:
                        left_finished = True
                if not right_finished:
                    if i + j < NS_lane_count:
                        ti_list.append(i + j)
                    else:
                        right_finished = True
                if left_finished and right_finished:
                    break
            table['Et' + str(i)] = ti_list
            table['Wt' + str(i)] = ti_list
        return table

    def get_ex_lane_list(self, ap_arm, turn_dir, ap_lane):
        if turn_dir == 't':
            return self.ex_lane_table[ap_arm + turn_dir + str(ap_lane)]
        else:
            return self.ex_lane_table[ap_arm + turn_dir]

    def gen_veh_dots(self, veh_wid, veh_len, veh_len_front, static_buf, time_buf):
        '''将车辆取成足够密的一个个散点。车辆的车头朝北，xy与画图逻辑坐标系同，x向右，y向下。车辆的前轮中心在(0,0)的位置。返回取到的系列点的x和y。'''
        xs = np.arange(-veh_wid/2 - static_buf, veh_wid/2 + static_buf + 1e-1, 0.2)
        ys = np.arange(-veh_len_front - static_buf, veh_len - veh_len_front + 1e-1 + static_buf, 0.2)
        xx, yy = np.meshgrid(xs, ys)
        if time_buf > static_buf:
            xs_tb = np.arange(-veh_wid/2, veh_wid/2 + 1e-1, 0.2) # 车宽
            ys_tb_front = np.arange(-veh_len_front - time_buf, -veh_len_front - static_buf + 1e-1, 0.2)
            ys_tb_back = np.arange(veh_len - veh_len_front + static_buf, veh_len - veh_len_front + time_buf + 1e-1, 0.2)
            ys_tb = np.append(ys_tb_front, ys_tb_back)
            xx_tb, yy_tb = np.meshgrid(xs_tb, ys_tb)
            xx = np.append(xx, xx_tb)
            yy = np.append(yy, yy_tb)
        return [xx.flatten(), yy.flatten()]

    def check_request(self, message): 
        # confirm时返回reservation，当reject时返回None
        ex_arm = Map.getInstance().get_ex_arm(message['arr_arm'], message['turn_dir'])
        ex_lane_list = self.get_ex_lane_list(message['arr_arm'], message['turn_dir'], message['arr_lane'])
        for ex_lane in ex_lane_list:
            ju_track = Map.getInstance().get_ju_track(message['arr_arm'], message['turn_dir'], message['arr_lane'], ex_lane)
            ju_shape_end_x = Track.cal_ju_shape_end_x(ju_track)
            # 加速到最高速度 - 匀速 方案
            acc_distance = (inter_v_lim**2 - message['arr_v']**2) / 2 / message['max_acc']
            if acc_distance >= ju_shape_end_x[-1]: 
                # 全程加速
                acc_acc = [[message['arr_t'], message['max_acc']]]
            else:
                # 加速-匀速
                acc_time = (inter_v_lim - message['arr_v']) / message['max_acc']
                acc_acc = [
                    [message['arr_t'], message['max_acc']], 
                    [message['arr_t'] + acc_time, 0]
                ]
            # 匀速方案
            if message['arr_v'] < inter_v_lim_min: # 速度小于 14.4 km/h，也就是 30 米的路口需要七八秒以上才能通过，太慢了
                acc_distance_c = (8**2 - message['arr_v']**2) / 2 / message['max_acc']
                if acc_distance_c >= ju_shape_end_x[-1]: 
                    acc_const_v = [[message['arr_t'], message['max_acc']]]
                else:
                    acc_time_c = (8 - message['arr_v']) / message['max_acc']
                    acc_const_v = [
                        [message['arr_t'], message['max_acc']], 
                        [message['arr_t'] + acc_time_c, 0]
                    ]
            else: # 速度不是过慢，这才能匀速
                acc_const_v = [[message['arr_t'], 0]]
            if self.check_cells_stepwise(message, ju_track, ju_shape_end_x, ex_arm, ex_lane, acc_acc):
                return {
                    'res_id': 0, # Todo
                    'ex_lane': ex_lane,
                    'arr_t': message['arr_t'],
                    'arr_v': message['arr_v'],
                    'acc': acc_acc
                }
            elif self.check_cells_stepwise(message, ju_track, ju_shape_end_x, ex_arm, ex_lane, acc_const_v):
                return {
                    'res_id': 0, # Todo
                    'ex_lane': ex_lane,
                    'arr_t': message['arr_t'],
                    'arr_v': message['arr_v'],
                    'acc': acc_const_v
                }
        return None
            
    def check_cells_stepwise(self, message, ju_track, ju_shape_end_x, ex_arm, ex_lane, acc):
        t = message['arr_t']
        v = message['arr_v']
        x_1d = 0
        a_idx = 0
        seg_idx = 0

        while x_1d <= ju_shape_end_x[-1]:
            # 计算车辆xy坐标和方向
            seg = ju_track[seg_idx]
            if seg_idx > 0:
                seg_x = x_1d - ju_shape_end_x[seg_idx - 1]  
            else:
                seg_x = x_1d
            if seg[0] == 'line': # 是直线
                if abs(seg[1][0] - seg[2][0]) < 1e-5: # 竖线
                    x = seg[1][0]
                    if seg[1][1] < seg[2][1]: # 从上到下
                        y = seg[1][1] + seg_x
                        angle = 180 # angle 是相比于“车头向北”顺时针旋转的度数
                    else: # 从下到上
                        y = seg[1][1] - seg_x
                        angle = 0
                else: # 横线 
                    y = seg[1][1]
                    if seg[1][0] < seg[2][0]: # 从左向右
                        x = seg[1][0] + seg_x
                        angle = 90 
                    else: # 从右向左
                        x = seg[1][0] - seg_x
                        angle = 270
            else: # 圆曲线
                if seg[5][0] < seg[5][1]: # 轨迹逆时针
                    rotation = seg[5][0] + seg_x / seg[4] * 180 / math.pi
                    angle = 180 - rotation
                    x = seg[3][0] + seg[4] * math.cos(-rotation / 180 * math.pi)
                    y = seg[3][1] + seg[4] * math.sin(-rotation / 180 * math.pi)
                else:
                    rotation = seg[5][0] - seg_x / seg[4] * 180 / math.pi
                    angle = - rotation
                    x = seg[3][0] + seg[4] * math.cos(-rotation / 180 * math.pi)
                    y = seg[3][1] + seg[4] * math.sin(-rotation / 180 * math.pi)
            
            # 计算在逻辑坐标系上车辆的dots的xy坐标(先旋转，再置于xy)
            veh_dots_x, veh_dots_y = self.gen_veh_dots(message['veh_wid'], message['veh_len'], message['veh_len_front'], \
                0.4, v * 0.1)
            veh_dots_x_rt = veh_dots_x * math.cos(angle*math.pi/180) - veh_dots_y * math.sin(angle*math.pi/180)
            veh_dots_y_rt = veh_dots_y * math.cos(angle*math.pi/180) + veh_dots_x * math.sin(angle*math.pi/180)
            veh_dots_x_rt += x
            veh_dots_y_rt += y
            
            # 利用grid.xy_to_ij转化为车辆此时占有的cell
            i, j = self.res_grid.xy_to_ij(veh_dots_x_rt, veh_dots_y_rt)
            t_slice = np.ones(i.shape, dtype=np.int16) * (round(t-self.res_grid.t_start))
            if t_slice[0] >= self.res_grid.cells.shape[2]:
                self.res_grid.add_time_dimension()
            
            # 检查占用的格点是否都空
            if np.sum(self.res_grid.cells[i, j, t_slice] != -1) == 0:
                self.res_grid.cells[i, j, t_slice] = message['veh_id']
            else:
                # 规划失败，清楚痕迹后返回False
                self.res_grid.clear_veh_cell(message['veh_id'])
                return False

            # 更新位置，速度，加速度，所在的形状
            x_1d += v * veh_dt + acc[a_idx][1] / 2 * veh_dt ** 2
            v += acc[a_idx][1] * veh_dt
            t += 1
            if a_idx+1 < len(acc) and t >= acc[a_idx+1][0]:
                a_idx += 1
            if x_1d > ju_shape_end_x[seg_idx]:
                seg_idx += 1 # 如果已经是最后一段形状的话，会退出循环的，没事

        occ_dura = max((v-inter_v_lim_min)/message['max_dec'] + message['veh_len']/v, min_gen_ht)
        occ_start = math.floor(t - (occ_dura / veh_dt))
        occ_end = math.ceil(t)
        for record in self.res_grid.ex_lane_record[ex_arm + str(ex_lane)]:
            if not (record[1] > occ_end or record[2] < occ_start):
                self.res_grid.clear_veh_cell(message['veh_id'])
                return False

        self.res_grid.ex_lane_record[ex_arm + str(ex_lane)].append([message['veh_id'], occ_start, occ_end])
        # logging.debug(str(self.res_grid.ex_lane_record[ex_arm + str(ex_lane)]))
        return True
    
class DresnerResGrid:
    '''a grid representation of intersection area'''
    def __init__(self, cell_size):
        self.lw = lane_width
        self.tr = turn_radius
        self.al = arm_len
        self.NSl = NS_lane_count
        self.EWl = EW_lane_count
        # 交叉口宽和高的一半，以 m 为单位，也就是 (x2, y2)
        self.wid_m_half = self.lw * self.NSl + self.tr
        self.hgt_m_half = self.lw * self.EWl + self.tr
        self.cell_size = cell_size
        # grid 的行数和列数
        self.i_n = math.ceil(self.hgt_m_half * 2 / cell_size) # 行数
        self.j_n = math.ceil(self.wid_m_half * 2 / cell_size) # 列数

        self.t_start = 0 # 第三维 t=0 对应的 timestep

        self.cells = - np.ones(shape=(self.i_n, self.j_n, int(20/veh_dt)), dtype=np.int16)
        self.ex_lane_record = self.init_ex_lane_record() # 这个是为了在出口道不相撞，每辆车到达之前的某段时间不可以有车到达

    def xy_to_ij(self, x_arr, y_arr):
        '''
        从 xy 坐标找对应的 cell index ij。xyij 都可以是向量。
        xy 坐标是 my_paint_canvas 中的逻辑坐标系，右、下分别为 x、y 正方向，原点位于交叉口中心
        ij 为第 i 行第 j 列。xy(-wid_m/2, -hgt_m/2) 对应于第 0 行 0 列的左上角。
        '''
        x_arr = np.array(x_arr)
        y_arr = np.array(y_arr)
        i_arr = np.zeros(y_arr.shape)
        j_arr = np.zeros(x_arr.shape)
        j_arr = np.floor((x_arr + self.wid_m_half) / self.cell_size).astype(np.int16)
        i_arr = np.floor((y_arr + self.hgt_m_half) / self.cell_size).astype(np.int16)
        i_arr[i_arr<0] = 0
        j_arr[j_arr<0] = 0
        i_arr[i_arr>=self.i_n] = self.i_n-1
        j_arr[j_arr>=self.j_n] = self.j_n-1
        return [i_arr, j_arr]

    def init_ex_lane_record(self):
        ex_lane_record = {}
        for i in range(NS_lane_count):
            ex_lane_record['N' + str(i)] = [] # 每个元素是[veh_id, occ_start, occ_end]
            ex_lane_record['S' + str(i)] = []
        for i in range(EW_lane_count):
            ex_lane_record['E' + str(i)] = []
            ex_lane_record['W' + str(i)] = []
        return ex_lane_record
    
    def clear_veh_cell(self, veh_id):
        '''清除某个车辆 veh_id 占用的所有格子'''
        self.cells[self.cells == veh_id] = -1

    def add_time_dimension(self):
        '''当第三维 t 不够用的时候直接把 size 翻倍'''
        self.cells = np.concatenate((self.cells, -np.ones(self.cells.shape, dtype=np.int16)), axis=2)
    
    def dispose_passed_time(self, timestep):
        '''把过去时间的信息都清除掉（反正也穿越不回去了）'''
        if timestep - self.t_start > 20:
            self.cells = self.cells[:, :, (timestep - self.t_start):]
            self.t_start = timestep
        for key, value in self.ex_lane_record.items():
            for record in value:
                if record[2] < timestep:
                    value.remove(record) # 删掉出口道里时间已过的信息

class XuManager(BaseInterManager):
    def __init__(self):
        super().__init__()
        self.veh_info = [] # 元素是(veh, report message)
        
    def receive_V2I(self, sender, message):
        if message['type'] == 'appear':
            self.update_topology()
        elif message['type'] == 'report':
            self.veh_info.append((sender, message))

    @staticmethod
    def is_conflict(ap_arm_dir_1, ap_arm_dir_2):
        return ap_arm_dir_1 in conflict_movements[ap_arm_dir_2]

    def update_topology(self):
        # 收集车辆位置信息
        self.veh_info.clear()
        ComSystem.I_broadcast({'type': 'request report'}) 
        # 按照 x 由大到小排序
        self.veh_info.sort(key=lambda e: -e[1]['inst_x']) 
        # 插入虚拟头车 0
        virtual_lead_x = self.veh_info[0][1]['inst_x'] + desired_cf_distance
        self.veh_info.insert(0, (None, {
            'inst_x': virtual_lead_x
        }))
        # 建立冲突图
        num_node = len(self.veh_info)
        cf_graph = nx.DiGraph()
        cf_graph.add_node(0, ap_arm_dir = 'Xx')
        for (i, info) in enumerate(self.veh_info):
            if i == 0:
                continue
            cf_graph.add_node(i, ap_arm_dir = info[1]['ap_arm'] + info[1]['turn_dir'])
            for j in range(1, i): # 前面的车 j
                if XuManager.is_conflict(
                    cf_graph.nodes[j]['ap_arm_dir'], 
                    cf_graph.nodes[i]['ap_arm_dir']
                ):
                    cf_graph.add_edge(j, i)
        for node in cf_graph.nodes:
            if node > 0 and cf_graph.in_degree(node) == 0:
                cf_graph.add_edge(0, node)
        # plt.subplot(131)
        # nx.draw_shell(cf_graph, with_labels=True, font_weight='bold')
        # 生成树
        tree = nx.DiGraph()
        tree.add_nodes_from(cf_graph)
        tree.nodes[0]['depth'] = 0
        for node in tree.nodes:
            if node == 0: 
                continue
            max_depth = 0
            max_depth_pred = 0
            for pred in cf_graph.predecessors(node):
                if tree.nodes[pred]['depth'] > max_depth: 
                    max_depth = tree.nodes[pred]['depth']
                    max_depth_pred = pred
            tree.nodes[node]['depth'] = max_depth + 1
            tree.add_edge(max_depth_pred, node)
        # plt.subplot(132)
        # nx.draw_shell(tree, with_labels=True, font_weight='bold')
        # 通信拓扑，这次是无向图，因为这里的通信都是双向的
        com_graph = nx.Graph(tree)
        nodes_same_depth = [[] for i in range(num_node)]
        max_depth = 0
        for node in com_graph.nodes:
            depth = com_graph.nodes[node]['depth']
            max_depth = max(depth, max_depth)
            nodes_same_depth[depth].append(node)
        nodes_same_depth = nodes_same_depth[0:max_depth+1]
        for node_list in nodes_same_depth:
            for i in range(len(node_list)):
                for j in range(i + 1, len(node_list), 1):
                    com_graph.add_edge(node_list[i], node_list[j])
        # plt.subplot(133)
        # nx.draw_shell(com_graph, with_labels=True, font_weight='bold')
        # plt.show()
        # 生成几个矩阵 A Q L
        A = nx.to_numpy_matrix(com_graph)
        A = np.asarray(A[1:, 1:]) # 这几个矩阵都是 [1, N]，不含 0
        nghbor_0 = list(nx.neighbors(com_graph, 0))
        diag = np.zeros(num_node)
        diag[nghbor_0] = 1
        diag = diag[1: ]
        Q = np.diag(diag)
        L = -A
        for i in range(num_node-1):
            L[i, i] = np.sum(A[i, :]) - A[i, i]
        L_plus_Q = L + Q
        # print('L+Q=%s' % str(L_plus_Q))
        # 将协调结果传给车
        for (i, info) in enumerate(self.veh_info):
            if i == 0:
                continue
            neighbor_index = np.where(L_plus_Q[i-1, :] != 0)[0] # i 是 node 编号，在这几个矩阵里 index 要小 1 
            # print('%d, neightbor_index=%s' % (i, str(neighbor_index)))
            neighbor_list = [self.veh_info[int(n+1)][0] for n in neighbor_index]
            l_q_list = L_plus_Q[i-1, neighbor_index]
            # print('L+Q=%s' % str(l_q_list))
            message = {
                'type': 'coordination',
                'self_depth': tree.nodes[i]['depth'], 
                'virtual_lead_x': virtual_lead_x, 
                'virtual_lead_v': virtual_lead_v, 
                'neighbor_list': neighbor_list, 
                'l_q_list': l_q_list
            }
            ComSystem.I2V(info[0], message)

# 根据设置选择某个实现
if inter_control_mode == 'traffic light':
    inter_manager = TrafficLightManager()
elif inter_control_mode == 'Dresner':
    inter_manager = DresnerManager()
elif inter_control_mode == 'Xu':
    inter_manager = XuManager()

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
        # logging.debug(str(message))
        for group, vehs in simulator.Simulator.getInstance().all_veh.items():
            for veh in vehs:
                veh.receive_broadcast(message)
        
