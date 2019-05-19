# Dresner 2008 multiagent
+ area 250 m × 250 m, intersection located at the center 
+ intersection size determined by the number of lanes, which is variable

Each step: 
1. Probabilistically spawns new vehicles
2. *Provides sensor input to all vehicles*
3. Allows all driver agents to act
4. Updates the position of all vehicles according to the physical model
5. Removes any vehicles outside the simulated area that have completed their journey

Vehicles:
+ Vehicle Identification Number (VIN)
+ Length, Width
+ *Distance from front of vehicle to front axle*
+ *Distance from front of vehicle to rear axle*
+ max v, max a, min a, *max steer angle, sensor range*
+ Position
+ Velocity
+ *Heading*
+ Acceleration
+ *Steering angle*

driver agent may access several simulated external sensors: 
+ a list of all vehicles within the sensor range, 我直接给了车辆的前车，反正他也不关心后车
+ a simplified laser range finder, 我直接给了前车，就知道它的位置了

+ *lane keeping 我这里可以省略掉我觉得，横向直接控制就好了*
+ *optimistic / pessimistic 见 algorithm3 把它跟IDM结合一下吧*
    + An optimistic agent makes a reservation assuming it will arrive at the intersection in the minimum possible time
    + finds itself no longer stuck behind a slower vehicle will become optimistic and attempt to make a new, earlier reservation
    + pessimistic agent assumes it will be stuck at its current velocity until it reaches the intersection
    + has to cancel its reservation because there is no way for it to arrive on time, it becomes pessimistic

+ *arrival time estimation* 

*model vehicle planar vehicle kinematics: dx/dt, dy/dt, d orientation/dt  可以算转弯半径的，我这里省了*

**delay**: 
+ When the vehicle is removed from simulation, its total delay is calculated 
+ compare the delays of all vehicles to delays using a policy that allows vehicles through the intersection unhindered

message:
+ Driver agents can send: Request, *Change-Request, (all properties) Cancel,* and Done (only VID)
+ Intersection send: 
    + Confirm: a unique identifier for the reservation, a start time, a start lane, a departure lane, restrictions on acc
    + Reject
    + Acknowledge: to Cancel and Done
    + *Emergency-Stop*

```python
request_message = {
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
}

change_request_message = {
    'type': 'change_request',
    'veh_id': veh._id, 
    'arr_t': 0, 
    'arr_v': 0, 
    'arr_arm': self.track.ap_arm,
    'arr_lane': ap_lane, 
    'turn_dir': veh.track.turn_dir, 
    'veh_len': veh.veh_len, 
    'veh_wid': veh.veh_wid
}

cancel_message = {
    'type': 'cancel', 
    'veh_id': 0, 
    'res_id': 0
}

done_message = {
    'type': 'done',
    'veh_id': 0, 
    'res_id': 0
}

confirm_message = {
    'type': 'confirm',
    'reservation': {
        'res_id': 0, 
        'ex_lane': 0,
        'arr_t': 0,
        'arr_v': 0,
        'acc': [
            [start_time1, acc1], 
            [start_time2, acc2]
        ]
    }
}

reject_message = {
    'type': 'reject',
    'timeout': 1
}

acknowledge_message = {
    'type': 'acknowledge',
    'res_id': 0
}
```

Outbound Lane: determine, priority 左右转先找最近的lane，直行找对应的 
Acceleration: 两种 profile，先是加速到最大然后保持，再是按照那个速度匀速通过
*Reservation Distance: 这个估计不一定靠谱*
*timeout: 挺不错的*
**edge tile: 打补丁的做法很粗暴，或许我直接在出口道设置个时间间隔就好了**

full simulator: 
+ 3 lanes in each of the 4 cardinal directions
+ *turn with probability 0.1, left = right 我这里还是自己调参数吧*
+ right lane -> turn right, etc
+ increasing granularity beyond twice the number of lanes can improve performance even more 

'''
对于合适的出口道列表：（左转：012..., 右转：...210，直行：l, l+1, l-1...)
    从map里通过get_ju_track拿到track
    试两种策略：加速到最高-匀速 / 匀速
        每一步：
            计算车辆xy坐标和方向
            计算在逻辑坐标系上车辆的dots的xy坐标(先旋转，再置于xy)
            利用grid.xy_to_ij转化为车辆此时占有的cell
            检查这些cell是否都为-1
            if 是:
                占据这些cell
            else: 
                用grid.clear_veh_cell清除这辆车的预约（之前算的时候标记的）
                本次规划失败
'''

    



            


