
import math

'''
A - 起点
B - 终点
ap_arm - approach arm, 'NSEW'
dir - direction, 'lrt'
'''
def gen_traj(xa, ya, xb, yb, ap_arm, dir):
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








    


        

