import yaml
import math

from map import Map
from simulator import Simulator
from lib.settings import lane_width, turn_radius, arm_len, NS_lane_count, EW_lane_count, veh_dt, disp_dt, simu_t, time_wrap

from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF, QLineF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtWidgets import QWidget

class MyPaintCanvas(QWidget):
    def __init__(self, parent=None, mainw=None):
        super().__init__(parent)
        self.mainw = mainw

        self.disp_timer = QTimer(self)
        self.disp_timer.start(disp_dt * 1000)
        self.disp_timer.timeout.connect(self.update)  # 每次 update 触发 paintEvent
        self.veh_timer = QTimer(self)
        self.veh_timer.start(veh_dt * 1000 / time_wrap)
        self.veh_timer.timeout.connect(self.update_traffic)

        self.lw = lane_width
        self.tr = turn_radius
        self.al = arm_len
        self.NSl = NS_lane_count
        self.EWl = EW_lane_count

        self.draw_road_shape = self.gen_draw_road()
        self.draw_traj_shape = self.gen_draw_traj(Map.getInstance().ju_track_table)

        # 设置背景颜色
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(247, 232, 232))
        self.setPalette(palette)

    def update_traffic(self):
        Simulator.getInstance().update()

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
        # self.draw_traj(qp) # 显示轨迹，调试用
        self.draw_vehs(qp)

        ts = Simulator.getInstance().timestep
        self.mainw.step_lbl.setText("Timestep: %4d" % ts)
        self.mainw.time_lbl.setText("Elapsed time: %.1f s" % (ts * veh_dt))
        # print('ts = %d, simu_t/veh_dt = %d' % (ts, simu_t / veh_dt))
        if ts >= simu_t / veh_dt:
            self.mainw.close()
    
    def gen_draw_road(self):
        '''
        在逻辑坐标系中，计算交叉口绘制所需的形状
        '''
        x1 = self.lw * self.NSl
        x2 = x1 + self.tr 
        x3 = x2 + self.al
        y1 = self.lw * self.EWl
        y2 = y1 + self.tr
        y3 = y2 + self.al
        edge_Qlines = [
            QLineF(-x3, -y1, -x2, -y1),  # 西上
            QLineF(-x3, y1, -x2, y1),    # 西下
            QLineF(x3, -y1, x2, -y1),    # 东上
            QLineF(x3, y1, x2, y1),      # 东下
            QLineF(-x1, -y3, -x1, -y2),  # 北左
            QLineF(x1, -y3, x1, -y2),    # 北右
            QLineF(-x1, y3, -x1, y2),    # 南左
            QLineF(x1, y3, x1, y2)       # 南右
        ]
        edge_Qarcs = [
            [QRectF(-x2-self.tr, -y2-self.tr, 2*self.tr, 2*self.tr), 270 * 16, 90 * 16], # 左上
            [QRectF(x1, -y2-self.tr, 2*self.tr, 2*self.tr), 180 * 16, 90 * 16], # 右上
            [QRectF(-x2-self.tr, y1, 2*self.tr, 2*self.tr), 0 * 16, 90 * 16], # 左下
            [QRectF(x1, y1, 2*self.tr, 2*self.tr), 90 * 16, 90 * 16] # 右下
        ]
        center_Qlines = [
            QLineF(-x3, 0, -x2, 0),       # 西
            QLineF(x3, 0, x2, 0),         # 东
            QLineF(0, -y3, 0, -y2),       # 北
            QLineF(0, y3, 0, y2)          # 南
        ]
        stop_Qlines = [
            QLineF(-x2, 0, -x2, y1),          # 西
            QLineF(x2, 0, x2, -y1),           # 东
            QLineF(0, -y2, -x1, -y2),         # 北
            QLineF(0, y2, x1, y2)             # 南
        ]
        lane_Qlines = []
        if self.EWl > 1:
            for i in range(self.EWl - 1):
                lane_Qlines.append(QLineF(-x3, - (i+1) * self.lw, -x2, - (i+1) * self.lw)) # 西上
                lane_Qlines.append(QLineF(-x3, (i+1) * self.lw, -x2, (i+1) * self.lw))     # 西下
                lane_Qlines.append(QLineF(x3, - (i+1) * self.lw, x2, - (i+1) * self.lw))   # 东上
                lane_Qlines.append(QLineF(x3, (i+1) * self.lw, x2, (i+1) * self.lw))       # 东下
        if self.NSl > 1:
            for i in range(self.NSl - 1):
                lane_Qlines.append(QLineF(- (i+1) * self.lw, -y3, - (i+1) * self.lw, -y2)) # 北左
                lane_Qlines.append(QLineF((i+1) * self.lw, -y3, (i+1) * self.lw, -y2))     # 北右
                lane_Qlines.append(QLineF(- (i+1) * self.lw, y3, - (i+1) * self.lw, y2))   # 南左
                lane_Qlines.append(QLineF((i+1) * self.lw, y3, (i+1) * self.lw, y2))       # 南右
        return {
            'edge_Qlines': edge_Qlines,
            'edge_Qarcs': edge_Qarcs,
            'center_Qlines': center_Qlines,
            'lane_Qlines': lane_Qlines,
            'stop_Qlines': stop_Qlines
        }

    def gen_draw_traj(self, ju_track_table):
        '''
        根据轨迹，生成用于画图的lines和arcs
        '''
        traj_Qlines = []
        traj_Qarcs = []
        for dir, shape_list in ju_track_table.items():
            for seg in shape_list:
                if seg[0] == 'line':
                    traj_Qlines.append(QLineF(seg[1][0], seg[1][1], seg[2][0], seg[2][1]))
                else:
                    traj_Qarcs.append([
                        QRectF(seg[3][0]-seg[4], seg[3][1]-seg[4], 2*seg[4], 2*seg[4]), 
                        min(seg[5][0], seg[5][1]) * 16, 
                        math.fabs(seg[5][0] - seg[5][1]) * 16
                    ])
        return {
            'traj_Qlines': traj_Qlines,
            'traj_Qarcs': traj_Qarcs
        }

    def draw_road(self, qp):
        # 交叉口边缘
        qp.setPen(QPen(QColor(49, 58, 135), 0.4, Qt.SolidLine))
        for ele in self.draw_road_shape['edge_Qlines']:
            qp.drawLine(ele)
        for ele in self.draw_road_shape['edge_Qarcs']:
            qp.drawArc(ele[0], ele[1], ele[2])                      

        # 车道中心线
        qp.setPen(QPen(QColor(242, 184, 0), 0.3, Qt.SolidLine))
        for ele in self.draw_road_shape['center_Qlines']:
            qp.drawLine(ele)

        # 车道线
        qp.setPen(QPen(QColor("white"), 0.2, Qt.SolidLine))
        for ele in self.draw_road_shape['lane_Qlines']:
            qp.drawLine(ele)

        # 停车线
        qp.setPen(QPen(QColor(244, 82, 79), 0.4, Qt.SolidLine))
        for ele in self.draw_road_shape['stop_Qlines']:
            qp.drawLine(ele)

    def draw_traj(self, qp):
        qp.setPen(QPen(QColor('darkGrey'), 0.2, Qt.SolidLine))
        for ele in self.draw_traj_shape['traj_Qlines']:
            qp.drawLine(ele)
        for ele in self.draw_traj_shape['traj_Qarcs']:
            qp.drawArc(ele[0], ele[1], ele[2]) 
    
    def draw_vehs(self, qp):
        qp.setBrush(QColor(49, 58, 135))
        qp.setPen(QPen(QColor(255, 152, 146), 0.1, Qt.SolidLine))
        qf = qp.font()
        qf.setPointSizeF(2.5)
        qf.setFamily('Consolas')
        qp.setFont(qf)
        x1 = self.lw * self.NSl
        x2 = x1 + self.tr 
        y1 = self.lw * self.EWl
        y2 = y1 + self.tr
        for veh in Simulator.getInstance().all_veh['Nap']: 
            x = - (self.lw / 2 + self.lw * veh.inst_lane)
            y = - (y2 + (-veh.inst_x))
            rect = QRectF(x - veh.veh_wid/2, y - veh.veh_len_back, veh.veh_wid, veh.veh_len)
            qp.drawRect(rect)
            # qp.drawText(rect.bottomLeft(), str(veh._id))
        for veh in Simulator.getInstance().all_veh['Nex']: 
            x = self.lw / 2 + self.lw * veh.inst_lane
            y = - (y2 + (veh.inst_x))
            rect = QRectF(x - veh.veh_wid/2, y - veh.veh_len_front, veh.veh_wid, veh.veh_len)
            qp.drawRect(rect)
            # qp.drawText(rect.bottomLeft(), str(veh._id))
        for veh in Simulator.getInstance().all_veh['Sap']:
            x = self.lw / 2 + self.lw * veh.inst_lane
            y = y2 + (-veh.inst_x)
            rect = QRectF(x - veh.veh_wid/2, y - veh.veh_len_front, veh.veh_wid, veh.veh_len)
            qp.drawRect(rect)
            # qp.drawText(rect.bottomLeft(), str(veh._id))
        for veh in Simulator.getInstance().all_veh['Sex']:
            x = - (self.lw / 2 + self.lw * veh.inst_lane)
            y = y2 + veh.inst_x
            rect = QRectF(x - veh.veh_wid/2, y - veh.veh_len_back, veh.veh_wid, veh.veh_len)
            qp.drawRect(rect)
            # qp.drawText(rect.bottomLeft(), str(veh._id))
        for veh in Simulator.getInstance().all_veh['Wap']:
            x = - (x2 + (-veh.inst_x))
            y = self.lw / 2 + self.lw * veh.inst_lane
            rect = QRectF(x - veh.veh_len_back, y - veh.veh_wid/2, veh.veh_len, veh.veh_wid)
            qp.drawRect(rect)
            # qp.drawText(rect.bottomLeft(), str(veh._id))
        for veh in Simulator.getInstance().all_veh['Wex']:
            x = - (x2 + veh.inst_x)
            y = - (self.lw / 2 + self.lw * veh.inst_lane)
            rect = QRectF(x - veh.veh_len_front, y - veh.veh_wid/2, veh.veh_len, veh.veh_wid)
            qp.drawRect(rect)
            # qp.drawText(rect.bottomLeft(), str(veh._id))
        for veh in Simulator.getInstance().all_veh['Eap']:
            x = x2 + (-veh.inst_x)
            y = - (self.lw / 2 + self.lw * veh.inst_lane)
            rect = QRectF(x - veh.veh_len_front, y - veh.veh_wid/2, veh.veh_len, veh.veh_wid)
            qp.drawRect(rect)
            # qp.drawText(rect.bottomLeft(), str(veh._id))
        for veh in Simulator.getInstance().all_veh['Eex']:
            x = x2 + veh.inst_x
            y = self.lw / 2 + self.lw * veh.inst_lane
            rect = QRectF(x - veh.veh_len_back, y - veh.veh_wid/2, veh.veh_len, veh.veh_wid)
            qp.drawRect(rect)
            # qp.drawText(rect.bottomLeft(), str(veh._id))
        for veh in Simulator.getInstance().all_veh['ju']:
            # 寻找在哪一段上 
            seg_idx = 0
            for (i, end_x) in enumerate(veh.track.ju_shape_end_x): 
                if veh.inst_x > end_x: # 比第i段的终点大，则在(i+1)段
                    seg_idx = i + 1
                    break
            seg = veh.track.ju_track[seg_idx] # 这一段的形状
            if seg_idx > 0:
                seg_x = veh.inst_x - veh.track.ju_shape_end_x[seg_idx - 1] # 在这一段的长度
            else:
                seg_x = veh.inst_x
            if seg[0] == 'line': # 是直线，太好了
                if abs(seg[1][0] - seg[2][0]) < 1e-5: # 竖线
                    x = seg[1][0]
                    if seg[1][1] < seg[2][1]: # 从上到下
                        y = seg[1][1] + seg_x
                        rect = QRectF(x - veh.veh_wid/2, y - veh.veh_len_back, veh.veh_wid, veh.veh_len)
                        qp.drawRect(rect)
                        # qp.drawText(rect.bottomLeft(), str(veh._id))
                    else: # 从下到上
                        y = seg[1][1] - seg_x
                        rect = QRectF(x - veh.veh_wid/2, y - veh.veh_len_front, veh.veh_wid, veh.veh_len)
                        qp.drawRect(rect)
                        # qp.drawText(rect.bottomLeft(), str(veh._id))
                else: # 横线 
                    y = seg[1][1]
                    if seg[1][0] < seg[2][0]: # 从左向右
                        x = seg[1][0] + seg_x
                        rect = QRectF(x - veh.veh_len_back, y - veh.veh_wid/2, veh.veh_len, veh.veh_wid)
                        qp.drawRect(rect)
                        # qp.drawText(rect.bottomLeft(), str(veh._id))
                    else: # 从右向左
                        x = seg[1][0] - seg_x
                        rect = QRectF(x - veh.veh_len_front, y - veh.veh_wid/2, veh.veh_len, veh.veh_wid)
                        qp.drawRect(rect)
                        # qp.drawText(rect.bottomLeft(), str(veh._id))
            else: # 圆曲线
                qp.save()
                qp.translate(seg[3][0], seg[3][1])
                if seg[5][0] < seg[5][1]: # 轨迹逆时针
                    rotation = seg[5][0] + seg_x / seg[4] * 180 / math.pi
                    qp.rotate(- rotation) # rotate 是顺时针的度数
                    rect = QRectF(seg[4] - veh.veh_wid/2, - veh.veh_len_front, veh.veh_wid, veh.veh_len)
                    qp.drawRect(rect)
                    # qp.drawText(rect.bottomLeft(), str(veh._id))
                else:
                    rotation = seg[5][0] - seg_x / seg[4] * 180 / math.pi
                    qp.rotate(- rotation)
                    rect = QRectF(seg[4] - veh.veh_wid/2, - veh.veh_len_back, veh.veh_wid, veh.veh_len)
                    qp.drawRect(rect)
                    # qp.drawText(rect.bottomLeft(), str(veh._id))
                qp.restore()