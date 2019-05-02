import yaml

# from traffic_flow import TrafficFlow

from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF, QLineF
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QWidget

class MyPaintCanvas(QWidget):
    def __init__(self, parent=None, mainw=None):
        super().__init__(parent)
        self.mainw = mainw

        self.disp_timer = QTimer(self)
        self.disp_timer.start(0.025 * 1000)
        self.disp_timer.timeout.connect(self.update)  # 每次 update 触发 paintEvent
        self.veh_timer = QTimer(self)
        self.veh_timer.start(0.2 * 1000)
        self.veh_timer.timeout.connect(self.update_traffic)

        self.load_scene_cfg()
        self.draw_road_shape = self.cal_draw_road()
        # self.traffic = TrafficFlow()
        self.veh_time_step = 0

        # 设置背景颜色
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(247, 232, 232))
        self.setPalette(palette)



    def load_scene_cfg(self):
        with open('res/scene.yaml', encoding='utf-8') as scene_cfg_file:
            scene_cfg = yaml.load(scene_cfg_file, Loader=yaml.FullLoader)
            self.lw = scene_cfg['lane_width']
            self.tr = scene_cfg['turn_radius']
            self.al = scene_cfg['arm_len']
            self.NSl = scene_cfg['NS_lanes']
            self.EWl = scene_cfg['EW_lanes']

    def update_traffic(self):
        # self.traffic.update_all_veh(self.veh_time_step)        
        self.veh_time_step += 1 
        # print('update_traffic: %f s' % (time.time() - t0))

    def paintEvent(self, event): # 每次 disp_timer timeout 的时候调用，重绘
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing, True)  # 消除锯齿

        window_wid = (self.lw * self.NSl + self.tr + self.al) * 2
        window_hgt = (self.lw * self.EWl + self.tr + self.al) * 2
        if window_hgt / self.height() < window_wid / self.width(): 
            # 高度方向比较宽松，宽度顶满
            viewport_wid = self.width()
            viewport_hgt = self.width() * window_hgt / window_wid
        else:
            # 宽度方向比较宽松，高度顶满
            viewport_wid = self.height() * window_wid / window_hgt 
            viewport_hgt = self.height()
        # setViewport(x, y, w, h) 设置视窗在控件上的坐标，这里居中
        qp.setViewport((self.width() - viewport_wid) / 2, (self.height() - viewport_hgt) / 2, viewport_wid, viewport_hgt)  
        # setWindow(x, y, w, h) 设置逻辑坐标，这里把中间点作为 (0, 0) 
        qp.setWindow(- window_wid / 2, - window_hgt / 2, window_wid, window_hgt)

        self.draw_road(qp)
        self.draw_vehs(qp)

        self.mainw.step_lbl.setText("Timestep: %4d" % self.veh_time_step)
        self.mainw.time_lbl.setText("Elapsed time: %.1f s" % (self.veh_time_step * 0.2))

    def cal_draw_road(self):
        '''
        在逻辑坐标系中计算交叉口绘制所需的形状参数
        '''
        x1 = self.lw * self.NSl
        x2 = x1 + self.tr 
        x3 = x2 + self.al
        y1 = self.lw * self.EWl
        y2 = y1 + self.tr
        y3 = y2 + self.al
        edge_lines = [
            QLineF(-x3, -y1, -x2, -y1),  # 西上
            QLineF(-x3, y1, -x2, y1),    # 西下
            QLineF(x3, -y1, x2, -y1),    # 东上
            QLineF(x3, y1, x2, y1),      # 东下
            QLineF(-x1, -y3, -x1, -y2),  # 北左
            QLineF(x1, -y3, x1, -y2),    # 北右
            QLineF(-x1, y3, -x1, y2),    # 南左
            QLineF(x1, y3, x1, y2)       # 南右
        ]
        edge_arcs = [
            [QRectF(-x2-self.tr, -y2-self.tr, 2*self.tr, 2*self.tr), 270 * 16, 90 * 16], # 左上
            [QRectF(x1, -y2-self.tr, 2*self.tr, 2*self.tr), 180 * 16, 90 * 16], # 右上
            [QRectF(-x2-self.tr, y1, 2*self.tr, 2*self.tr), 0 * 16, 90 * 16], # 左下
            [QRectF(x1, y1, 2*self.tr, 2*self.tr), 90 * 16, 90 * 16] # 右下
        ]
        center_lines = [
            QLineF(-x3, 0, -x2, 0),       # 西
            QLineF(x3, 0, x2, 0),         # 东
            QLineF(0, -y3, 0, -y2),       # 北
            QLineF(0, y3, 0, y2)          # 南
        ]
        stop_lines = [
            QLineF(-x2, 0, -x2, y1),          # 西
            QLineF(x2, 0, x2, -y1),           # 东
            QLineF(0, -y2, -x1, -y2),         # 北
            QLineF(0, y2, x1, y2)             # 南
        ]
        lane_lines = []
        if self.EWl > 1:
            for i in range(self.EWl - 1):
                lane_lines.append(QLineF(-x3, - (i+1) * self.lw, -x2, - (i+1) * self.lw)) # 西上
                lane_lines.append(QLineF(-x3, (i+1) * self.lw, -x2, (i+1) * self.lw))     # 西下
                lane_lines.append(QLineF(x3, - (i+1) * self.lw, x2, - (i+1) * self.lw))   # 东上
                lane_lines.append(QLineF(x3, (i+1) * self.lw, x2, (i+1) * self.lw))       # 东下
        if self.NSl > 1:
            for i in range(self.NSl - 1):
                lane_lines.append(QLineF(- (i+1) * self.lw, -y3, - (i+1) * self.lw, -y2)) # 北左
                lane_lines.append(QLineF((i+1) * self.lw, -y3, (i+1) * self.lw, -y2))     # 北右
                lane_lines.append(QLineF(- (i+1) * self.lw, y3, - (i+1) * self.lw, y2))   # 南左
                lane_lines.append(QLineF((i+1) * self.lw, y3, (i+1) * self.lw, y2))       # 南右
        return {
            'edge_lines': edge_lines,
            'edge_arcs': edge_arcs,
            'center_lines': center_lines,
            'lane_lines': lane_lines,
            'stop_lines': stop_lines
        }

    def draw_road(self, qp):
        # 交叉口边缘
        qp.setPen(QPen(QColor(49, 58, 135), 0.4, Qt.SolidLine))
        for ele in self.draw_road_shape['edge_lines']:
            qp.drawLine(ele)
        for ele in self.draw_road_shape['edge_arcs']:
            qp.drawArc(ele[0], ele[1], ele[2])                      

        # 车道中心线
        qp.setPen(QPen(QColor(242, 184, 0), 0.2, Qt.SolidLine))
        for ele in self.draw_road_shape['center_lines']:
            qp.drawLine(ele)

        # 车道线
        qp.setPen(QPen(QColor("white"), 0.2, Qt.SolidLine))
        for ele in self.draw_road_shape['lane_lines']:
            qp.drawLine(ele)

        # 停车线
        qp.setPen(QPen(QColor(244, 82, 79), 0.2, Qt.SolidLine))
        for ele in self.draw_road_shape['stop_lines']:
            qp.drawLine(ele)

    
    def draw_vehs(self, qp):
        pass

'''
    def draw(self, qp):
        if cfg['circular']: # 圆形只支持一条车道，因为多条车道会涉及每圈路程不同的问题
            qp.translate(self.logical_r, self.logical_r)  # 逻辑坐标系原点切换至正中间 
            
            # 画车道边缘 - 圆圈
            pen = QPen(QColor("darkGray"), 0.5, Qt.SolidLine)
            qp.setPen(pen)
            inner_r = self.ring_radius - 1.75
            outer_r = self.ring_radius + 1.75
            qp.drawEllipse(QPointF(0.0, 0.0), inner_r, inner_r)
            qp.drawEllipse(QPointF(0.0, 0.0), outer_r, outer_r)
            
            # 画车辆
            for vehicle in self.traffic.vehicles[0]:
                qp.save()
                qp.setBrush(self.get_color(vehicle.inst_v))
                qp.rotate(self.tr60 - vehicle.inst_x / self.ring_radius / np.pi * 180)
                qp.drawRect(QRectF(self.ring_radius - vehicle.veh_wid/2, - vehicle.veh_len/2, vehicle.veh_wid, vehicle.veh_len))
                qp.restore()
        else:
            
            
            # 画车辆
            lanecenter_bottom = - self.lw*self.NSl * (cfg['num_of_lanes'] - 1) / 2
            for lane in range(cfg['num_of_lanes']):
                for vehicle in self.traffic.vehicles[lane]:
                    qp.save()
                    qp.setBrush(QColor(80, 80, 80))
                    y = lanecenter_bottom + lane * self.lw*self.NSl - vehicle.veh_wid / 2
                    if vehicle.time_after_lc < 4:                           # 换道的过渡
                        y -= vehicle.last_lc_dir * (4 - vehicle.time_after_lc) / 4 * self.lw*self.NSl
                    qp.drawRect(QRectF(vehicle.inst_x - vehicle.veh_len / 2, y, vehicle.veh_len, vehicle.veh_wid))
                    qp.restore()
'''