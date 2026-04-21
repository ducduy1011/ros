#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import termios
import tty
import select
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


MSG = r"""
========================================
TELEOP MECANUM 4 BÁNH (PLANAR MOVE)
========================================

Điều khiển tịnh tiến:
   q    w    e
   a    s    d
   z    x    c

q : chéo lên trái
w : đi thẳng
e : chéo lên phải
a : sang trái
s : dừng
d : sang phải
z : chéo xuống trái
x : đi lùi
c : chéo xuống phải

Xoay tại chỗ:
j : xoay trái
l : xoay phải

Tăng/giảm tốc độ:
u : tăng tốc tuyến tính
o : giảm tốc tuyến tính
i : tăng tốc quay
k : giảm tốc quay

Khác:
space / s : dừng
Ctrl+C    : thoát
========================================
"""

class MecanumTeleopKeyboard(Node):
    def __init__(self) -> None:
        super().__init__("mecanum_teleop_keyboard")

        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)

        self.declare_parameter("linear_speed", 0.30)
        self.declare_parameter("angular_speed", 0.80)
        self.declare_parameter("linear_step", 0.05)
        self.declare_parameter("angular_step", 0.10)
        self.declare_parameter("max_linear_speed", 1.00)
        self.declare_parameter("max_angular_speed", 2.50)
        self.declare_parameter("hold_accel_step", 0.08)
        self.declare_parameter("hold_max_multiplier", 3.0)
        self.declare_parameter("hold_timeout", 0.8)

        self.linear_speed = float(self.get_parameter("linear_speed").value)
        self.angular_speed = float(self.get_parameter("angular_speed").value)
        self.linear_step = float(self.get_parameter("linear_step").value)
        self.angular_step = float(self.get_parameter("angular_step").value)
        self.max_linear_speed = float(self.get_parameter("max_linear_speed").value)
        self.max_angular_speed = float(self.get_parameter("max_angular_speed").value)
        self.hold_accel_step = float(self.get_parameter("hold_accel_step").value)
        self.hold_max_multiplier = float(self.get_parameter("hold_max_multiplier").value)
        self.hold_timeout = float(self.get_parameter("hold_timeout").value)

        self.last_move_key = ""
        self.last_move_time = 0.0
        self.hold_multiplier = 1.0

        self.get_logger().info("Mecanum teleop keyboard started")
        self.get_logger().info(
            f"Initial speeds -> linear: {self.linear_speed:.2f} m/s, "
            f"angular: {self.angular_speed:.2f} rad/s"
        )

    def publish_cmd(self, vx: float, vy: float, wz: float) -> None:
        msg = Twist()
        msg.linear.x = float(vx)
        msg.linear.y = float(vy)
        msg.linear.z = 0.0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = float(wz)
        self.pub.publish(msg)

    def stop_robot(self) -> None:
        self.publish_cmd(0.0, 0.0, 0.0)

    def clamp_speeds(self) -> None:
        self.linear_speed = max(0.0, min(self.linear_speed, self.max_linear_speed))
        self.angular_speed = max(0.0, min(self.angular_speed, self.max_angular_speed))

    def print_speed(self) -> None:
        print(
            f"\rTốc độ gốc -> tuyến tính: {self.linear_speed:.2f} m/s | "
            f"quay: {self.angular_speed:.2f} rad/s | giữ phím để tăng dần theo hệ số xN        "
        )

    def reset_hold_acceleration(self) -> None:
        self.last_move_key = ""
        self.last_move_time = 0.0
        self.hold_multiplier = 1.0

    def build_cmd_with_hold_accel(
        self,
        key: str,
        x_cmd: float,
        y_cmd: float,
        z_cmd: float,
    ) -> tuple[float, float, float]:
        now = time.monotonic()
        if key == self.last_move_key and (now - self.last_move_time) <= self.hold_timeout:
            self.hold_multiplier = min(
                self.hold_multiplier + self.hold_accel_step,
                self.hold_max_multiplier,
            )
        else:
            self.hold_multiplier = 1.0

        self.last_move_key = key
        self.last_move_time = now

        vx = x_cmd * self.linear_speed * self.hold_multiplier
        vy = y_cmd * self.linear_speed * self.hold_multiplier
        wz = z_cmd * self.angular_speed * self.hold_multiplier

        vx = max(-self.max_linear_speed, min(vx, self.max_linear_speed))
        vy = max(-self.max_linear_speed, min(vy, self.max_linear_speed))
        wz = max(-self.max_angular_speed, min(wz, self.max_angular_speed))
        return vx, vy, wz

def get_key(settings) -> str:
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    key = sys.stdin.read(1) if rlist else ""
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main() -> None:
    settings = termios.tcgetattr(sys.stdin)

    rclpy.init()
    node = MecanumTeleopKeyboard()

    move_bindings = {
        "w": ( 1.0,  0.0,  0.0),
        "x": (-1.0,  0.0,  0.0),
        "a": ( 0.0,  1.0,  0.0),
        "d": ( 0.0, -1.0,  0.0),
        "q": ( 1.0,  1.0,  0.0),
        "e": ( 1.0, -1.0,  0.0),
        "z": (-1.0,  1.0,  0.0),
        "c": (-1.0, -1.0,  0.0),
        "j": ( 0.0,  0.0,  1.0),
        "l": ( 0.0,  0.0, -1.0),
        "s": ( 0.0,  0.0,  0.0),
        " ": ( 0.0,  0.0,  0.0),
    }

    print(MSG)
    node.print_speed()

    try:
        while True:
            key = get_key(settings)

            if key in move_bindings:
                x_cmd, y_cmd, z_cmd = move_bindings[key]
                if key in ("s", " "):
                    node.reset_hold_acceleration()
                    vx, vy, wz = 0.0, 0.0, 0.0
                else:
                    vx, vy, wz = node.build_cmd_with_hold_accel(key, x_cmd, y_cmd, z_cmd)
                node.publish_cmd(vx, vy, wz)

                print(
                    f"\rPhím: {key} | cmd_vel = "
                    f"(x={vx:.2f}, y={vy:.2f}, wz={wz:.2f}) | x{node.hold_multiplier:.2f}               "
                )

            elif key == "u":
                node.reset_hold_acceleration()
                node.linear_speed += node.linear_step
                node.clamp_speeds()
                node.print_speed()

            elif key == "o":
                node.reset_hold_acceleration()
                node.linear_speed -= node.linear_step
                node.clamp_speeds()
                node.print_speed()

            elif key == "i":
                node.reset_hold_acceleration()
                node.angular_speed += node.angular_step
                node.clamp_speeds()
                node.print_speed()

            elif key == "k":
                node.reset_hold_acceleration()
                node.angular_speed -= node.angular_step
                node.clamp_speeds()
                node.print_speed()

            elif key == "\x03":
                break

    except Exception as exc:
        print(f"\nLỗi teleop: {exc}")

    finally:
        node.stop_robot()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()
        print("\nĐã thoát teleop.")

if __name__ == "__main__":
    main()