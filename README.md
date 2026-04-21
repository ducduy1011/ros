# my_robot_description

Goi ROS 2 mo ta robot banh mecanum 4 banh, kem mo phong Gazebo, hien thi RViz va node dieu khien bang ban phim.

## 1. Tong quan

Project hien tai da co:

- Mo hinh robot URDF xuat tu SolidWorks: `urdf/Assem1_4.urdf`.
- Mesh 3D cho than, banh, lidar, imu va cac chi tiet co khi.
- Mo phong Gazebo voi:
  - Plugin cmd_vel/odom (planar move).
  - Cam bien IMU topic `/imu/data`.
  - Cam bien lidar topic `/scan`.
- RViz config san: `rviz/sim.rviz`.
- Script teleop ban phim cho mecanum: `scripts/teleop_mecanum_keyboard.py`.
- Script chuyen `cmd_vel` sang toc do tung banh: `scripts/mecanum_cmdvel_to_wheels.py`.
- File controller YAML cho wheel velocity controller.

## 2. Cau truc chinh

- `launch/display.launch.py`: Mo URDF + joint_state_publisher_gui + RViz.
- `launch/sim.launch.py`: Chay Gazebo, spawn robot, robot_state_publisher, RViz.
- `config/controllers.yaml`: Khai bao `joint_state_broadcaster` va `wheel_velocity_controller`.
- `worlds/simple_obstacles.world`: Ban do vat can don gian (dang co san de mo rong).

## 3. Yeu cau moi truong

- Ubuntu + ROS 2 (khuyen nghi Humble).
- Cac goi can thiet:
  - `robot_state_publisher`
  - `joint_state_publisher`
  - `joint_state_publisher_gui`
  - `rviz2`
  - `gazebo_ros`
  - `tf2`
  - `controller_manager`
  - `ros2_control`
  - `ros2_controllers`
  - `gazebo_ros2_control`
  - `turtlebot3_gazebo` (vi file `sim.launch.py` dang su dung world cua turtlebot3)

Neu thieu package, cai bang apt theo ban phan phoi ROS 2 dang dung.

## 4. Build package

Chay tu workspace ROS 2 (vi du: `~/ros2_ws`):

```bash
cd ~/ros2_ws
colcon build --packages-select my_robot_description
source install/setup.bash
```

## 5. Cach chay nhanh de demo

### 5.1. Xem robot trong RViz (khong Gazebo)

```bash
ros2 launch my_robot_description display.launch.py
```

### 5.2. Chay mo phong Gazebo + RViz

```bash
ros2 launch my_robot_description sim.launch.py
```

Sau khi mo phong chay, robot se duoc spawn voi ten `my_robot`.

### 5.3. Dieu khien robot bang ban phim

Mo terminal moi (da source workspace), chay:

```bash
ros2 run my_robot_description teleop_mecanum_keyboard.py
```

## 6. Bang phim dieu khien

Layout phim:

```text
q    w    e
a    s    d
z    x    c
```

- Tinh tien:
  - `w`: di thang
  - `x`: di lui
  - `a`: sang trai
  - `d`: sang phai
  - `q/e/z/c`: di cheo
- Quay tai cho:
  - `j`: quay trai
  - `l`: quay phai
- Toc do:
  - `u/o`: tang giam toc do tuyen tinh
  - `i/k`: tang giam toc do quay
- Dung:
  - `s` hoac `space`

## 7. Topic quan trong de minh hoa cho giao vien

- Lenh dieu khien:
  - `/cmd_vel` (`geometry_msgs/Twist`)
- Odometry:
  - `/odom`
- IMU:
  - `/imu/data`
- Lidar:
  - `/scan`

Kiem tra nhanh:

```bash
ros2 topic list
ros2 topic echo /odom
ros2 topic echo /imu/data
ros2 topic echo /scan
```

## 8. Ve controllers va script chuyen cmd_vel -> wheel

Project da co:

- `config/controllers.yaml`
- `scripts/mecanum_cmdvel_to_wheels.py`

Script nay publish len topic:

- `/wheel_velocity_controller/commands`

Huu ich khi ban muon dieu khien toc do tung banh qua ros2_control. Trong phien ban hien tai, mo phong da co plugin planar move nhan truc tiep `/cmd_vel`, nen van co the demo di chuyen ngay ma khong can buoc controller nay.

## 9. Noi dung co the trinh bay trong 2-3 phut

- Day la robot mecanum 4 banh tu model CAD (SolidWorks -> URDF).
- Da tich hop mo phong Gazebo va quan sat RViz.
- Da tich hop cam bien IMU + lidar trong mo phong.
- Da co teleop ban phim de dieu khien cac huong va quay tai cho.
- Da dat nen tang cho huong mo rong: ros2_control, dieu khien toc do tung banh, va world co vat can.

## 10. Tac gia

- Package: `my_robot_description`
- Maintainer trong package: `acer`
