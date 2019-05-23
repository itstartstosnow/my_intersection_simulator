# 信号灯单车道均衡

## log 2019-05-22 20-45-53
[150, 'Nl', 'Nt', 'Nr'], 
[150, 'Sl', 'St', 'Sr'], 
[150, 'El', 'Et', 'Er'], 
[150, 'Wl', 'Wt', 'Wr']
yellow_time = 1.5
45, 90, 45 = 180
phase time 150

veh_not_finish_min = 27
actual_total_flow = 634
avg_delay = 27.79
max_delay = 50.67

## log 2019-05-22 20-50-06
90, 180, 90 = 360
phase time 150

veh_not_finish_min = 55
actual_total_flow = 1218
avg_delay = 30.77
max_delay = 66.07

```
log 2019-05-22 20-54-26 略了
90, 180, 90 = 360
phase time 150 -> 200 ts
veh_not_finish_min = 39
actual_total_flow = 962
avg_delay = 40.19
max_delay = 89.37
```

## log 2019-05-22 20-58-24
180, 360, 180 = 720
phase time 200 ts

veh_not_finish_min = 59
actual_total_flow = 1363
avg_delay = 45.44
max_delay = 99.80


# Xu 单车道均衡

## log 2019-05-22 14-54-44
NS_lane_count = 1
EW_lane_count = 1
45, 90, 45 = 180
desired_cf_distance = 25
kp = 0.15
kv = 0.7

veh_not_finish_min = 32
actual_total_flow = 840
avg_delay = 3.17
max_delay = 11.64

## log 2019-05-22 15-08-13
90, 180, 90 = 360

veh_not_finish_min = 63
actual_total_flow = 1586
avg_delay = 6.31
max_delay = 14.74

## log 2019-05-22 15-13-36
180, 360, 180 = 720

veh_not_finish_min = 86
actual_total_flow = 2150
avg_delay = 16.46
max_delay = 42.32
delay 明显增大

## log 2019-05-22 17-37-17
270, 540, 270 = 1080

veh_not_finish_min = 84
actual_total_flow = 2057
avg_delay = 28.05
max_delay = 56.20
delay 先大后小

# DResner 单车道均衡

## log 2019-05-22 20-19-07
45, 90, 45 = 180

veh_not_finish_min = 33
actual_total_flow = 735
avg_delay = 1.76
max_delay = 4.32

## log 2019-05-22 19-42-08
90, 180, 90 = 360

veh_not_finish_min = 60
actual_total_flow = 1330
avg_delay = 2.98
max_delay = 13.61

## log 2019-05-22 19-47-03
180, 360, 180 = 720

veh_not_finish_min = 99
actual_total_flow = 2177
avg_delay = 6.36
max_delay = 30.32

## log 2019-05-22 17-49-46
arm_len = 100 默认值
270, 540, 270 = 1080

veh_not_finish_min = 127
actual_total_flow = 2792
avg_delay = 21.58
max_delay = 61.90

```
log 2019-05-22 17-44-00 略了
arm_len = 200
270, 540, 270 = 1080
veh_not_finish_min = 110
actual_total_flow = 2624
avg_delay = 31.83
max_delay = 77.28
```

# 信号灯单车道不均衡

## log 2019-05-23 00-22-23
80, 160, 160, 320 = 180 * 4
100, 190, 190, 380 timestep

veh_not_finish_min = 24
actual_total_flow = 631
avg_delay = 38.17
max_delay = 76.27

## log 2019-05-23 00-28-56
160, 320, 320, 640 = 360 * 4
100, 190, 190, 380 timestep

veh_not_finish_min = 29
actual_total_flow = 661
avg_delay = 31.00
max_delay = 72.75

## log 2019-05-23 10-11-13
320, 640, 640, 1280 = 720 * 4

veh_not_finish_min = 36
actual_total_flow = 819
avg_delay = 38.23
max_delay = 81.33


# Xu 单车道不均衡

## log 2019-05-23 00-38-08
80, 160, 160, 320 = 180 * 4

veh_not_finish_min = 22
actual_total_flow = 544
avg_delay = 3.78
max_delay = 9.32

## log 2019-05-23 00-34-03
160, 320, 320, 640 = 360 * 4

veh_not_finish_min = 63
actual_total_flow = 1541
avg_delay = 6.53
max_delay = 13.77
看起来效果还挺漂亮的

## log 2019-05-23 00-42-10
320, 640, 640, 1280 = 720 * 4

veh_not_finish_min = 125
actual_total_flow = 3050
avg_delay = 10.90
max_delay = 27.32

## log 2019-05-23 00-54-44
400, 800, 800, 1600 = 900 * 4 = 3600

veh_not_finish_min = 103
actual_total_flow = 2529
avg_delay = 18.85
max_delay = 43.99


# Dresner 单车道不均衡

## log 2019-05-23 00-59-42
80, 160, 160, 320 = 180 * 4

veh_not_finish_min = 34
actual_total_flow = 769
avg_delay = 1.81
max_delay = 5.41

## log 2019-05-23 01-04-33
160, 320, 320, 640 = 360 * 4

veh_not_finish_min = 64
actual_total_flow = 1420
avg_delay = 2.98
max_delay = 9.12

## log 2019-05-23 01-08-37
320, 640, 640, 1280 = 720 * 4
veh_not_finish_min = 116
actual_total_flow = 2558
avg_delay = 6.73
max_delay = 20.12

## log 2019-05-23 01-12-51
400, 800, 800, 1600 = 900 * 4 = 3600

veh_not_finish_min = 130
actual_total_flow = 2921
avg_delay = 14.14
max_delay = 34.58