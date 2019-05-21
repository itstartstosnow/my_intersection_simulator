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

# BaseManager
```
+ BaseInterManagerupdate()
+ receive_V2I(sender, message)
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