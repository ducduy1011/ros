# Hướng dẫn mở và chạy bài my_robot_description

Em là sinh viên thực hiện bài này. File này chỉ ghi cách mở và chạy để thầy xem nhanh, không trình bày lý thuyết.

## 1. Thông tin nhanh

- Tên package: my_robot_description
- Workspace em dùng: ~/ros2_ws
- Mô hình chính: urdf/Assem1_4.urdf
- Launch để chạy mô phỏng: launch/sim.launch.py
- Launch để xem model nhanh trên RViz: launch/display.launch.py

## 2. Mở workspace và build

Mở terminal, chạy đúng thứ tự:

```bash
cd ~/ros2_ws
colcon build --packages-select my_robot_description
source install/setup.bash
```

Nếu đã build trước đó thì vẫn nên source lại:

```bash
source ~/ros2_ws/install/setup.bash
```

## 3. Cách chạy để xem bài (khuyên dùng)

### Bước 1: Mở mô phỏng Gazebo + RViz

Terminal 1:

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 launch my_robot_description sim.launch.py
```

Sau khi chạy lệnh trên, robot sẽ xuất hiện trong Gazebo (entity: my_robot) và RViz cũng mở sẵn cấu hình.

### Bước 2: Điều khiển robot bằng bàn phím

Mở Terminal 2:

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 run my_robot_description teleop_mecanum_keyboard.py
```

## 4. Phím điều khiển

Các phím di chuyển:

```text
q    w    e
a    s    d
z    x    c
```

- w: đi thẳng
- x: đi lùi
- a: sang trái
- d: sang phải
- q, e, z, c: đi chéo
- j: quay trái tại chỗ
- l: quay phải tại chỗ
- s hoặc space: dừng

Chỉnh tốc độ:

- u/o: tăng hoặc giảm tốc độ tịnh tiến
- i/k: tăng hoặc giảm tốc độ quay

## 5. Cách kiểm tra nhanh bài đang chạy đúng

Mở Terminal 3 (tuỳ chọn), chạy:

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 topic list
```

Nếu chạy đúng sẽ thấy các topic chính như:

- /cmd_vel
- /odom
- /imu/data
- /scan

Có thể kiểm tra dữ liệu cảm biến:

```bash
ros2 topic echo /imu/data
ros2 topic echo /scan
```

## 6. Trường hợp muốn mở model nhanh, không chạy Gazebo

Terminal:

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 launch my_robot_description display.launch.py
```

## 7. Lỗi thường gặp và cách xử lý nhanh

- Lỗi không tìm thấy package:
  - Chưa source workspace. Chạy lại: source ~/ros2_ws/install/setup.bash
- Mở launch nhưng không thấy robot:
  - Đóng hết terminal cũ, chạy lại từ Bước 1 theo đúng thứ tự.
- Bấm phím không chạy:
  - Nhớ click vào terminal đang chạy teleop để terminal nhận bàn phím.

## 8. Nội dung nộp

Trong package hiện có đủ các phần để thầy chạy kiểm tra:

- URDF và mesh robot
- Launch file cho RViz và Gazebo
- Teleop bàn phím
- Cấu hình RViz
- Cấu hình controller

Em xin cảm ơn thầy đã xem bài.
