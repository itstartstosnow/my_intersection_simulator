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
        # self.traffic = TrafficFlow()
        self.veh_time_step = 0

    def load_scene_cfg(self):
        with open('res/scene.yaml', encoding='utf-8') as scene_cfg_file:
            scene_cfg = yaml.load(scene_cfg_file, Loader=yaml.FullLoader)
            self.lw = scene_cfg['lane_width']
            self.tr = scene_cfg['turn_radius']
            self.al = scene_cfg['arm_len']

    def update_traffic(self):
        # self.traffic.update_all_veh(self.veh_time_step)        
        self.veh_time_step += 1 
        # print('update_traffic: %f s' % (time.time() - t0))

    def paintEvent(self, event): # 每次 disp_timer timeout 的时候调用，重绘
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing, True)  # 消除锯齿

        viewport_len = min(self.width(), self.height())
        qp.setViewport(0, 0, viewport_len, viewport_len) # 设置视窗正方形区域
        window_len = (self.lw + self.tr + self.al) * 2
        qp.setWindow(0, 0, window_len, window_len)

        self.draw_lane(qp)
        self.draw_vehs(qp)

        self.mainw.step_lbl.setText("Timestep: %4d" % self.veh_time_step)
        self.mainw.time_lbl.setText("Elapsed time: %.1f s" % (self.veh_time_step * 0.2))

    def draw_lane(self, qp):
        qp.translate(self.lw + self.tr + self.al, self.lw + self.tr + self.al)

        # 交叉口边缘
        qp.setPen(QPen(QColor("darkGrey"), 0.1, Qt.SolidLine))
        qp.drawLine(QLineF(-self.tr-self.lw-self.al, -self.lw, -self.tr-self.lw, -self.lw))  # 西上
        qp.drawLine(QLineF(-self.tr-self.lw-self.al, self.lw, -self.tr-self.lw, self.lw))    # 西下
        qp.drawLine(QLineF(self.tr+self.al+self.lw, -self.lw, self.tr+self.lw, -self.lw))    # 东上
        qp.drawLine(QLineF(self.tr+self.al+self.lw, self.lw, self.tr+self.lw, self.lw))      # 东下
        qp.drawLine(QLineF(-self.lw, -self.tr-self.al-self.lw, -self.lw, -self.tr-self.lw))  # 北左
        qp.drawLine(QLineF(self.lw, -self.tr-self.al-self.lw, self.lw, -self.tr-self.lw))    # 北右
        qp.drawLine(QLineF(-self.lw, self.tr+self.al+self.lw, -self.lw, self.tr+self.lw))    # 南左
        qp.drawLine(QLineF(self.lw, self.tr+self.al+self.lw, self.lw, self.tr+self.lw))      # 南右
        qp.drawArc(QRectF(-self.lw-2*self.tr, -self.lw-2*self.tr, 2*self.tr, 2*self.tr), 270 * 16, 90 * 16) # 左上
        qp.drawArc(QRectF(self.lw, -self.lw-2*self.tr, 2*self.tr, 2*self.tr), 180 * 16, 90 * 16)            # 右上
        qp.drawArc(QRectF(-self.lw-2*self.tr, self.lw, 2*self.tr, 2*self.tr), 0 * 16, 90 * 16)              # 左下
        qp.drawArc(QRectF(self.lw, self.lw, 2*self.tr, 2*self.tr), 90 * 16, 90 * 16)                        # 右下

        # 车道中心线
        qp.setPen(QPen(QColor("darkGrey"), 0.05, Qt.SolidLine))
        qp.drawLine(QLineF(-self.tr-self.al-self.lw, 0, -self.tr-self.lw, 0))         # 西
        qp.drawLine(QLineF(self.tr+self.al+self.lw, 0, self.tr+self.lw, 0))           # 东
        qp.drawLine(QLineF(0, -self.tr-self.al-self.lw, 0, -self.tr-self.lw))         # 北
        qp.drawLine(QLineF(0, self.tr+self.al+self.lw, 0, self.tr+self.lw))           # 南

        # 停车线
        qp.setPen(QPen(QColor("lightGrey"), 0.2, Qt.SolidLine))
        qp.drawLine(QLineF(-self.tr-self.lw, 0, -self.tr-self.lw, self.lw))          # 西
        qp.drawLine(QLineF(self.tr+self.lw, 0, self.tr+self.lw, -self.lw))           # 东
        qp.drawLine(QLineF(0, -self.tr-self.lw, -self.lw, -self.tr-self.lw))         # 北
        qp.drawLine(QLineF(0, self.tr+self.lw, self.lw, self.tr+self.lw))            # 南
    
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
            lanecenter_bottom = - self.lw * (cfg['num_of_lanes'] - 1) / 2
            for lane in range(cfg['num_of_lanes']):
                for vehicle in self.traffic.vehicles[lane]:
                    qp.save()
                    qp.setBrush(QColor(80, 80, 80))
                    y = lanecenter_bottom + lane * self.lw - vehicle.veh_wid / 2
                    if vehicle.time_after_lc < 4:                           # 换道的过渡
                        y -= vehicle.last_lc_dir * (4 - vehicle.time_after_lc) / 4 * self.lw
                    qp.drawRect(QRectF(vehicle.inst_x - vehicle.veh_len / 2, y, vehicle.veh_len, vehicle.veh_wid))
                    qp.restore()
'''