#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from pynput import keyboard
import sys
import termios # 터미널 설정을 제어하기 위한 모듈

class KeyTeleopNode(Node):
    def __init__(self):
        super().__init__('key_teleop_node')
        self.publisher = self.create_publisher(Twist, 'car1/cmd_vel', 1)

        self.target_linear = 0.0
        self.target_steering = 0.0
        self.max_steering = 0.6
        self.max_velocity = 5.55
        self.pressed_keys = {'w': False, 's': False, 'a': False, 'd': False}
        self.timer = self.create_timer(0.05, self.timer_callback)

    def timer_callback(self):
        if self.pressed_keys['w']: 
            self.target_linear += 0.05
        elif self.pressed_keys['s']: 
            self.target_linear -= 0.05
        else:
            linear_decay = 0.1
            if self.target_linear > 0.0:
                self.target_linear = max(0.0, self.target_linear - linear_decay)
            elif self.target_linear < 0.0:
                self.target_linear = min(0.0, self.target_linear + linear_decay)

        if self.pressed_keys['a']: 
            self.target_steering += 0.1
        elif self.pressed_keys['d']: 
            self.target_steering -= 0.1
        else:
            steering_decay = 0.1
            if self.target_steering > 0.0:
                self.target_steering = max(0.0, self.target_steering - steering_decay)
            elif self.target_steering < 0.0:
                self.target_steering = min(0.0, self.target_steering + steering_decay)

        self.target_steering = max(min(self.target_steering, self.max_steering), -self.max_steering)
        self.target_linear = max(min(self.target_linear, self.max_velocity), -self.max_velocity)

        cmd_msg = Twist()
        cmd_msg.linear.x = self.target_linear
        
        if self.target_linear < 0.0:
            cmd_msg.angular.z = -self.target_steering
        else:
            cmd_msg.angular.z = self.target_steering
        self.publisher.publish(cmd_msg)

def main(args=None):
    # ---------------------------------------------------
    # [핵심] 스크립트 실행 중 터미널의 문자 출력(Echo) 끄기
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    new_settings = termios.tcgetattr(fd)
    new_settings[3] = new_settings[3] & ~termios.ECHO # ECHO 플래그 제거
    termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
    # ---------------------------------------------------

    rclpy.init(args=args)
    node = KeyTeleopNode()

    def on_press(key):
        try:
            char = key.char
            if char in node.pressed_keys:
                node.pressed_keys[char] = True
            elif char == 'q':
                return False
        except AttributeError:
            if key == keyboard.Key.space:
                node.target_linear = 0.0
                node.target_steering = 0.0
            elif key == keyboard.Key.esc:
                return False

    def on_release(key):
        try:
            char = key.char
            if char in node.pressed_keys:
                node.pressed_keys[char] = False
        except AttributeError:
            pass

    print("🎮 게임 모드 텔레옵이 활성화되었습니다! (입력 숨김 적용됨)")
    print("w/a/s/d : 꾹 누르고 있으면 가속/조향이 부드럽게 연속으로 변합니다.")
    print("SPACE   : 즉시 정지 (초기화)")
    print("q / ESC : 안전하게 종료")

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    try:
        while listener.running and rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        # 1. 차량 강제 정지
        stop_msg = Twist()
        node.publisher.publish(stop_msg)
        
        # 2. 노드 종료
        node.destroy_node()
        rclpy.shutdown()
        
        # 3. [중요] 스크립트 종료 시 터미널 설정을 원래대로 복구!
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == '__main__':
    main()