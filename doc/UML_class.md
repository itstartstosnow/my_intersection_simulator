# MyMainWindow(QMainWindow)
```
+ icons: dict
+ main_widget: QWidget
+ canvas: MyPaintCanvas

+ setup_menubar()
+ setup_toolbar()
+ setup_statusbar()
+ play_triggered()
+ fileQuit()
+ closeEvent()
+ about()
```

# MyPaintCanvas(QWidget)
```
+ mainw: MyMainWindow
+ disp_timer: QTimer
+ veh_timer: QTimer
+ draw_road_shape: dict
+ draw_traj_shape: dict

+ gen_draw_road(): dict
+ gen_draw_traj(ju_track_table): dict
+ update_traffic()
+ paintEvent(event)
+ draw_road(qp)
+ draw_vehs(qp)
```

# Map
```
+ lw: float
+ tr: float
+ al: float
+ NSl: int
+ EWl: int
+ ju_track_table: dict
+ ex_arm_table: dict

+ get_ex_arm(ap_arm, turn_dir): string
+ get_ju_track(ap_arm, turn_dir, ap_lane, ex_lane): list
+ gen_ju_track_table()
+ gen_ju_track(xa, ya, xb, yb, ap_arm, dir): list
```

# Track
```
+ ap_arm: string
+ ap_lane: int
+ turn_dir: string
+ ju_track: list
+ ex_arm: string
+ ex_lane: int
+ is_complete: bool
+ ju_shape_end_x: list

+ confirm_ex_lane(ex_lane)
+ cal_ju_shape_end_x(ju_track)
```

# BaseVehicle
```
+ _id: int
+ veh_wid: float
+ veh_len: float
+ veh_len_front: float
+ veh_len_back: float
+ max_v: float
+ max_acc: float
+ max_dec:float
+ track: Track
+ timestep: int
+ inst_a: float
+ inst_v: float
+ zone: string
+ inst_lane: int
+ inst_x: float
+ cf_model: CFModel

- __eq__(vehicle): bool
+ acc_with_lead_veh(lead_veh): float
+ update_control(lead_veh)
+ update_position(dt): bool
```

# CFModel
```
+ v0: float
+ T: float
+ s0: float
+ a: float
+ b: float
+ delta: float

+ acc_from_model(v, s, v_l): float
```

# HumanDrivenVehicle
```
+ traffic_light: string
+ cf_v0_backup: float
+ cf_T_backup: float

+ update_control(lead_veh)
+ update_position(dt): bool
+ receive_broadcast(self, message)
```

# DresnerVehicle
```
+ reservation: dict
+ timeout: float
+ optimism: bool
+ ap_acc_profile: list

+ plan_arr(): list
+ update_control(lead_veh)
+ update_position(lead_veh): bool
+ receive_I2V(message)
```

# XuVehicle
```
+ reported: bool
+ depth: int
+ virtual_lead_x: float
+ virtual_lead_v: float
+ neighbor_list: list
+ l_q_list: list

+ update_control(lead_veh)
+ acc_from_feedback(): float
+ update_position(dt): bool
+ receive_I2V(message)
+ receive_broadcast(message)
```

# ComSystem
```
+ V2V(receiver, sender, message)
+ V2I(sender, message)
+ I2V(receiver, message)
+ I_broadcast(message)
```

# Simulator
```
+ timestep: int
+ gen_veh_count: int
+ point_queue_table: dict
+ all_veh: dict

+ update()
+ all_update_position(): list
+ update_group(to_switch_group)
+ remove_out_veh()
+ init_point_queue_table()
+ gen_new_veh()
+ make_veh(ap_arm, ap_lane, turn_dir)
+ update_all_control()
```


# BaseInterManager
```
+ timestep: int

+ update()
+ receive_V2I(sender, message)
```

# TrafficLightManager
```
+ current_phase: int 
+ current_elapsed_time: int
+ phase: list

+ update()
+ update_phase()
```
 
# DresnerManager
```
+ res_grid: DresnerResGrid
+ ex_lane_table: dict
+ res_registery: dict

+ update()
+ receive_V2I(sender, message)
+ gen_ex_lane_table()
+ get_ex_lane_list(ap_arm, turn_dir, ap_lane)
+ gen_veh_dots(veh_wid, veh_len, veh_len_front, static_buf, time_buf)
+ check_request(message)
+ check_cells_stepwise(message, ju_track, ju_shape_end_x, ex_arm, ex_lane, acc)
```

# XuManager
```
+ veh_info: list

+ receive_V2I(sender, message)
+ is_conflict(ap_arm_dir_1, ap_arm_dir_2): bool
+ update_topology()
```

# DresnerResGrid 组合关系
```
+ lw: float
+ tr: float
+ al: float
+ NSl: int
+ EWl: int
+ wid_m_half: float
+ hig_m_half: float
+ cell_size: float
+ i_n: int
+ j_n: int
+ t_start: int
+ cells: np.ndarray
+ ex_lane_record: dict

+ xy_to_ij(x_arr, y_arr): list
+ init_ex_lane_record(): dict
+ clear_veh_cell(veh_id)
+ add_time_dimension()
+ dispose_passed_time(timestep)
```

# 注
Comsystem的地方比较乱
