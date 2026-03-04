#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist

import sys, select, termios, tty
import threading

settings = termios.tcgetattr(sys.stdin)

def get_key():
    tty.setraw(sys.stdin.fileno())

    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

class KeyTeleopNode(Node):
    def __init__(self):
        super().__init__('key_teleop_node')
        
        self.publisher = self.create_publisher(Twist, 'car1/cmd_vel', 1)

        self.target_linear = 0.0
        self.target_steering = 0.0
        self.max_steering = 0.6

        self.timer = self.create_timer(0.02, self.timer_callback)

    def timer_callback(self):

        cmd_msg = Twist()
        cmd_msg.linear.x = self.target_linear
        cmd_msg.angular.z = self.target_steering
        self.publisher.publish(cmd_msg)

        
def main(args=None):
    rclpy.init(args=args)

    key_teleop_node = KeyTeleopNode()

    spin_thread = threading.Thread(target=rclpy.spin, args=(key_teleop_node,))
    spin_thread.start()

    msg = """
    Control Your Car!
    ---------------------------
    Moving around:
             w    
        a    s    d
    
    SPACE : Force stop
    q : Quit
    """
    print(msg)

    try:
        while True:
            key = get_key()

            if key == 'w':
                key_teleop_node.target_linear += 0.1
            elif key == 's':
                key_teleop_node.target_linear -= 0.1
            elif key == 'a':
                key_teleop_node.target_steering += 0.1
            elif key == 'd':
                key_teleop_node.target_steering -= 0.1
            elif key == ' ':
                key_teleop_node.target_linear = 0.0
                key_teleop_node.target_steering = 0.0
            elif key == 'q' or key == '\x03':
                break

            key_teleop_node.target_steering = max(min(key_teleop_node.target_steering, key_teleop_node.max_steering), -key_teleop_node.max_steering)
    except Exception as e:
        print(e)

    finally:
        stop_msg = Twist()
        stop_msg.linear.x = 0.0
        stop_msg.angular.z = 0.0
        key_teleop_node.publisher.publish(stop_msg)

        key_teleop_node.destroy_node()
        rclpy.shutdown()
        spin_thread.join()

if __name__ == '__main__':
    main()
