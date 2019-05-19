车辆进入时报告 appear， 交叉口存到 next group 里面

当 next group 的头车进入到内圈的时候 报告 enter 

交叉口收到 next group 有个车进入内圈的情况
就对 next group 的进行组织 
发 request report 请求每辆车的位置之类的
车辆收到 request report，就会 report 自己的情况
他们的虚拟头车应该是当前group的最后一辆 要慢 
他们变成了 current group

next group 清空 

## 信息类型
```python
# 车辆发交叉口
message = {
    'type': 'appear'
}

message = {
    'type': 'enter'
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
    'lead_veh': None
}


```