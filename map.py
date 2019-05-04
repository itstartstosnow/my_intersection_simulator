import math

from lib.settings import lane_width, turn_radius, arm_len, NS_lane_count, EW_lane_count, allowed_arm_turn

class Map:
    _instance = None

    @staticmethod 
    def getInstance():
        if Map._instance == None:
            Map()
        return Map._instance

    def __init__(self):
        if Map._instance != None:
            raise Exception("This class is a singleton, but more than one objects are created.")
        else:
            Map._instance = self

        self.lw = lane_width
        self.tr = turn_radius
        self.al = arm_len
        self.NSl = NS_lane_count
        self.EWl = EW_lane_count

        self.ju_track_table = self.gen_ju_track_table()
        self.ex_arm_table = {
            'Nl': 'E', 'Nt': 'S', 'Nr': 'W', 
            'Sl': 'W', 'St': 'N', 'Sr': 'E', 
            'El': 'S', 'Et': 'W', 'Er': 'N',
            'Wl': 'N', 'Wt': 'E', 'Wr': 'S'
        }
    
    def get_ex_arm(ap_arm, turn_dir):
        return ex_arm_table[str(ap_arm) + str(turn_dir)]

    def gen_ju_track_table(self):
        '''generate vehicle tracks in junction area.'''
        x1 = self.lw * self.NSl
        x2 = x1 + self.tr 
        y1 = self.lw * self.EWl
        y2 = y1 + self.tr

        ju_track_table = {}
        # 转弯的情况
        for i in range(self.EWl): # 从/到东西
            for j in range(self.NSl): # 从/到南北
                x4 = self.lw / 2 + self.lw * j   # 始/末位置的x坐标绝对值
                y4 = self.lw / 2 + self.lw * i   # 始/末位置的y坐标绝对值
                # 从东西方向到南北方向
                ju_track_table['Wl'+str(i)+str(j)] = gen_ju_track(xa=-x2, ya=y4, xb=x4, yb=-y2, ap_arm='W', dir='l')
                ju_track_table['Wr'+str(i)+str(j)] = gen_ju_track(xa=-x2, ya=y4, xb=-x4, yb=y2, ap_arm='W', dir='r')
                ju_track_table['El'+str(i)+str(j)] = gen_ju_track(xa=x2, ya=-y4, xb=-x4, yb=y2, ap_arm='E', dir='l')
                ju_track_table['Er'+str(i)+str(j)] = gen_ju_track(xa=x2, ya=-y4, xb=x4, yb=-y2, ap_arm='E', dir='r')
                # 从南北方向到东西方向
                ju_track_table['Nl'+str(j)+str(i)] = gen_ju_track(xa=-x4, ya=-y2, xb=x2, yb=y4, ap_arm='N', dir='l')
                ju_track_table['Nr'+str(j)+str(i)] = gen_ju_track(xa=-x4, ya=-y2, xb=-x2, yb=-y4, ap_arm='N', dir='r')
                ju_track_table['Sl'+str(j)+str(i)] = gen_ju_track(xa=x4, ya=y2, xb=-x2, yb=-y4, ap_arm='S', dir='l')
                ju_track_table['Sr'+str(j)+str(i)] = gen_ju_track(xa=x4, ya=y2, xb=x2, yb=y4, ap_arm='S', dir='r')
        # 东西直行
        for i in range(self.EWl): # 从i道
            for j in range(self.EWl): # 到j道
                y_start = self.lw / 2 + self.lw * i # 起始位置y坐标绝对值
                y_end = self.lw / 2 + self.lw * j   # 结束位置y坐标绝对值
                ju_track_table['Wt'+str(i)+str(j)] = gen_ju_track(xa=-x2, ya=y_start, xb=x2, yb=y_end, ap_arm='W', dir='t')
                ju_track_table['Et'+str(i)+str(j)] = gen_ju_track(xa=x2, ya=-y_start, xb=-x2, yb=-y_end, ap_arm='E', dir='t')
        # 南北直行
        for i in range(self.NSl): # 从i道
            for j in range(self.NSl): # 到j道
                x_start = self.lw / 2 + self.lw * i # 起始位置x坐标绝对值
                x_end = self.lw / 2 + self.lw * j   # 结束位置x坐标绝对值
                ju_track_table['Nt'+str(i)+str(j)] = gen_ju_track(xa=-x_start, ya=-y2, xb=-x_end, yb=y2, ap_arm='N', dir='t')
                ju_track_table['St'+str(i)+str(j)] = gen_ju_track(xa=x_start, ya=y2, xb=x_end, yb=-y2, ap_arm='S', dir='t')
        table_filtered = {}
        for dir, shape_list in ju_track_table.items():
            for ele in allowed_arm_turn:
                if dir.startswith(ele):
                    table_filtered[dir] = shape_list
                    break

        # print(table_filtered)
        return table_filtered

def gen_ju_track(xa, ya, xb, yb, ap_arm, dir):
    '''
    生成起点为 A(xa, ya)，终点为 B(xb, yb)，来自 ap_arm 方向的车辆在 junction zone 的轨迹
        A - 起点
        B - 终点
        ap_arm - approach arm, 'NSEW'
        dir - direction, 'lrt'
    '''
    # 转弯，轨迹由相切的直线和圆曲线组成
    if dir == 'l' or dir == 'r':
        # 先根据转弯的方向，确定圆曲线的角度范围，角度的规定与数学中相同
        if ap_arm == 'N': 
            if dir == 'l':
                angle = (180, 270)
            else:
                angle = (360, 270)
        elif ap_arm == 'S': 
            if dir == 'l':
                angle = (0, 90)
            else:
                angle = (180, 90)
        elif ap_arm == 'E':
            if dir == 'l':
                angle = (90, 180)
            else:
                angle = (270, 180)
        elif ap_arm == 'W':
            if dir == 'l': 
                angle = (270, 360)
            else:
                angle = (90, 0)

        x_diff = abs(xb - xa)
        y_diff = abs(yb - ya)

        # 对于EW转向NS的车，直线段当x_diff小时出出现在终点附近，y_diff小时在起点附近
        if ap_arm == 'E' or ap_arm == 'W':
            # 只有个圆曲线
            if abs(x_diff - y_diff) < 1e-5: 
                center = [xa, yb]
                return [
                    ['arc', (xa, ya), (xb, yb), center, x_diff, angle] # 圆曲线，起点xy，终点xy，圆心，半径，角度始末
                ]
            # A - 直线 - 圆曲线 - B
            elif x_diff > y_diff: 
                if xa < xb:
                    junc = [xb - y_diff, ya]
                else: 
                    junc = [xb + y_diff, ya]
                center = [junc[0], yb]
                r = y_diff
                return [
                    ['line', (xa, ya), junc], # 直线，起点xy，终点xy
                    ['arc', junc, (xb, yb), center, r, angle] # 圆曲线，起点xy，终点xy，圆心，半径，角度始末
                ]
            # A - 圆曲线 - 直线 - B
            else: 
                if ya < yb:
                    junc = [xb, ya + x_diff]   
                else: 
                    junc = [xb, ya - x_diff]
                center = [xa, junc[1]]
                r = x_diff
                return [
                    ['arc', (xa, ya), junc, center, r, angle], # 圆曲线，起点xy，终点xy，圆心，半径，角度始末
                    ['line', junc, (xb, yb)] # 直线，起点xy，终点xy
                ]
        # 对于NS转向EW的车，直线段当x_diff小时出出现在起点附近，y_diff小时在终点附近
        elif ap_arm == 'N' or ap_arm == 'S': 
            # 只有个圆曲线
            if abs(x_diff - y_diff) < 1e-5: 
                center = [xb, ya]
                return [
                    ['arc', (xa, ya), (xb, yb), center, x_diff, angle] # 圆曲线，起点xy，终点xy，圆心，半径，角度始末
                ]
            # A - 圆曲线 - 直线 - B
            elif x_diff > y_diff: 
                if xa < xb:
                    junc = [xa + y_diff, yb]
                else: 
                    junc = [xa - y_diff, yb]
                center = [junc[0], ya]
                r = y_diff
                return [
                    ['arc', (xa, ya), junc, center, r, angle], # 圆曲线，起点xy，终点xy，圆心，半径，角度始末
                    ['line', junc, (xb, yb)] # 直线，起点xy，终点xy
                ]
            # A - 直线 - 圆曲线 - B
            else: 
                if ya < yb:
                    junc = [xa, yb - x_diff]   
                else: 
                    junc = [xa, yb + x_diff]
                center = [xb, junc[1]]
                r = x_diff
                return [
                    ['line', (xa, ya), junc], # 直线，起点xy，终点xy
                    ['arc', junc, (xb, yb), center, r, angle] # 圆曲线，起点xy，终点xy，圆心，半径，角度始末
                ]
    # 直行，轨迹由一条直线或相切的两条圆曲线组成
    elif dir == 't': 
        # 直行到与之对照的车道，直线轨迹即可
        if abs(xa - xb) < 1e-5 or abs(ya - yb) < 1e-5: 
            return [
                ['line', (xa, ya), (xb, yb)]
            ]
        # 车道不对应，由两条圆曲线组成
        elif ap_arm == 'N' or ap_arm == 'S':
            half_x_diff = abs(xa - xb) / 2
            half_y_diff = abs(ya - yb) / 2
            r = (half_x_diff ** 2 + half_y_diff ** 2) / (2 * half_x_diff)
            alpha = math.asin(half_y_diff / r) / math.pi * 180
            if ap_arm == 'S' and xb > xa:
                return [
                    ['arc', (xa, ya), ((xa+xb)/2, (ya+yb)/2), (xa + r, ya), r, (180, 180 - alpha)],
                    ['arc', ((xa+xb)/2, (ya+yb)/2), (xb, yb), (xb - r, yb), r, (360 - alpha, 360)]
                ]
            elif ap_arm == 'S' and xb < xa:
                return [
                    ['arc', (xa, ya), ((xa+xb)/2, (ya+yb)/2), (xa - r, ya), r, (0, alpha)],
                    ['arc', ((xa+xb)/2, (ya+yb)/2), (xb, yb), (xb + r, yb), r, (180 + alpha, 180)]
                ]
            elif ap_arm == 'N' and xb > xa: 
                return [
                    ['arc', (xa, ya), ((xa+xb)/2, (ya+yb)/2), (xa + r, ya), r, (180, 180 + alpha)],
                    ['arc', ((xa+xb)/2, (ya+yb)/2), (xb, yb), (xb - r, yb), r, (alpha, 0)]
                ]
            elif ap_arm == 'N' and xb < xa: 
                return [
                    ['arc', (xa, ya), ((xa+xb)/2, (ya+yb)/2), (xa - r, ya), r, (360, 360 - alpha)],
                    ['arc', ((xa+xb)/2, (ya+yb)/2), (xb, yb), (xb + r, yb), r, (180 - alpha, 180)]
                ]
        elif ap_arm == 'E' or ap_arm == 'W':
            half_x_diff = abs(xa - xb) / 2
            half_y_diff = abs(ya - yb) / 2
            r = (half_x_diff ** 2 + half_y_diff ** 2) / (2 * half_y_diff)
            alpha = math.asin(half_x_diff / r) / math.pi * 180
            if ap_arm == 'E' and ya > yb: 
                return [
                    ['arc', (xa, ya), ((xa+xb)/2, (ya+yb)/2), (xa, ya - r), r, (270, 270 - alpha)],
                    ['arc', ((xa+xb)/2, (ya+yb)/2), (xb, yb), (xb, yb + r), r, (90 - alpha, 90)]
                ]
            elif ap_arm == 'E' and ya < yb: 
                return [
                    ['arc', (xa, ya), ((xa+xb)/2, (ya+yb)/2), (xa, ya + r), r, (90, 90 + alpha)],
                    ['arc', ((xa+xb)/2, (ya+yb)/2), (xb, yb), (xb, yb - r), r, (270 + alpha, 270)]
                ]
            elif ap_arm == 'W' and ya > yb: 
                return [
                    ['arc', (xa, ya), ((xa+xb)/2, (ya+yb)/2), (xa, ya - r), r, (270, 270 + alpha)],
                    ['arc', ((xa+xb)/2, (ya+yb)/2), (xb, yb), (xb, yb + r), r, (90 + alpha, 90)]
                ]
            elif ap_arm == 'W' and ya < yb: 
                return [
                    ['arc', (xa, ya), ((xa+xb)/2, (ya+yb)/2), (xa, ya + r), r, (90, 90 - alpha)],
                    ['arc', ((xa+xb)/2, (ya+yb)/2), (xb, yb), (xb, yb - r), r, (270 - alpha, 270)]
                ]

class Track:
    def __init__(self, ju_shape_list):
        self.ju_shape_list = ju_shape_list
        self.x_end = self.cal_x_end
    
    def x_to_plane_coord(self, x):
        '''从线性坐标系的坐标 x (沿轨迹驶过的距离) 到逻辑坐标系的平面坐标'''
        pass

    def cal_x_end(self):
        pass

