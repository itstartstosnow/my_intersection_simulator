车辆进入时报告 appear
交叉口发 request report 请求每辆车的位置之类的
车辆收到 request report，就会 report 自己的情况
交叉口剔除掉已经进入交叉口的车，重新生成图、树和通信图
发送给每一辆车 coordination

## 信息类型
```python
# 车辆发交叉口
message = {
    'type': 'appear'
}

message = {
    'type': 'report', 
    'veh_id': self._id,
    'inst_x': self.inst_x, 
    'ap_arm': self.track.ap_arm,
    'ap_lane': self.track.ap_lane, 
    'turn_dir': self.track.turn_dir,
    'ex_lane': self.track.ex_lane
}

# 交叉口发车辆
message = {
    'type': 'request report'
}

message = {
    'type': 'coordination',
    'self_depth': 
    'virtual_lead_x': 
    'virtual_lead_v': 
    'neighbor_list': 
    'l_q_list': 
}
```

单车道，3.5m, 6m
左转路程 (1.75 + 3.5 + 6) * np.pi / 2 = 17.7
直行路程 (3.5 + 6) * 2 = 19
右转路程 (1.75 + 6) * np.pi / 2 = 12.2