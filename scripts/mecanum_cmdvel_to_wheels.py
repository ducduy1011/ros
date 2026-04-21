#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class MecanumCmdVelToWheels(Node):
    def __init__(self) -> None:
        super().__init__("mecanum_cmdvel_to_wheels")

        # Kích thước hình học robot
        self.declare_parameter("wheel_radius", 0.05)
        self.declare_parameter("wheel_base", 0.13)
        self.declare_parameter("track_width", 0.1952)
        self.declare_parameter("max_wheel_speed", 20.0)

        # Thứ tự bánh theo controller:
        # [trước trái, trước phải, sau trái, sau phải]
        self.declare_parameter("fl_multiplier", 1.0)
        self.declare_parameter("fr_multiplier", 1.0)
        self.declare_parameter("rl_multiplier", 1.0)
        self.declare_parameter("rr_multiplier", 1.0)

        self.wheel_radius = float(self.get_parameter("wheel_radius").value)
        self.wheel_base = float(self.get_parameter("wheel_base").value)
        self.track_width = float(self.get_parameter("track_width").value)
        self.max_wheel_speed = float(self.get_parameter("max_wheel_speed").value)

        self.fl_multiplier = float(self.get_parameter("fl_multiplier").value)
        self.fr_multiplier = float(self.get_parameter("fr_multiplier").value)
        self.rl_multiplier = float(self.get_parameter("rl_multiplier").value)
        self.rr_multiplier = float(self.get_parameter("rr_multiplier").value)

        self.commands_pub = self.create_publisher(
            Float64MultiArray,
            "/wheel_velocity_controller/commands",
            10,
        )

        self.create_subscription(Twist, "/cmd_vel", self.cmd_vel_cb, 10)
        self.get_logger().info("Mecanum planar controller started")
        self.get_logger().info(
            "Wheel order: [front_left, front_right, rear_left, rear_right]"
        )

    def cmd_vel_cb(self, msg: Twist) -> None:
        if math.isclose(self.wheel_radius, 0.0):
            self.get_logger().error("wheel_radius must be non-zero")
            return

        # Quy ước ROS chuẩn:
        #   linear.x  > 0 : đi thẳng
        #   linear.y  > 0 : sang trái
        #   angular.z > 0 : quay trái (CCW)
        vx = float(msg.linear.x)
        vy = float(msg.linear.y)
        wz = float(msg.angular.z)

        lx = self.wheel_base / 2.0
        ly = self.track_width / 2.0
        k = lx + ly
        r = self.wheel_radius

        # Động học nghịch mecanum đúng theo bảng điều khiển:
        # Đi thẳng:      [+ + + +]
        # Đi lùi:        [- - - -]
        # Sang phải:     [+ - - +]
        # Sang trái:     [- + + -]
        # Chéo lên phải: [+ 0 0 +]
        # Chéo lên trái: [0 + + 0]
        # Chéo xuống phải:[0 - - 0]
        # Chéo xuống trái:[- 0 0 -]
        # Xoay phải:     [+ - + -]
        # Xoay trái:     [- + - +]
        w_fl = (vx - vy - k * wz) / r
        w_fr = (vx + vy + k * wz) / r
        w_rl = (vx + vy - k * wz) / r
        w_rr = (vx - vy + k * wz) / r

        wheels = [
            w_fl * self.fl_multiplier,
            w_fr * self.fr_multiplier,
            w_rl * self.rl_multiplier,
            w_rr * self.rr_multiplier,
        ]

        limited = [
            max(-self.max_wheel_speed, min(self.max_wheel_speed, v)) for v in wheels
        ]

        cmd = Float64MultiArray()
        cmd.data = limited
        self.commands_pub.publish(cmd)

        self.get_logger().debug(
            f"cmd_vel => vx={vx:.3f}, vy={vy:.3f}, wz={wz:.3f} | wheels={limited}"
        )


def main() -> None:
    rclpy.init()
    node = MecanumCmdVelToWheels()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()