import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
import sys, select, termios, tty

msg = """
-----------------------------------------
체커봇 제어 모드:
-----------------------------------------
[주행 제어]        [체커보드 제어]
    w                 u : 위로 (Rail Up)
a   s   d             j : 아래로 (Rail Down)
                      i : 시계 방향 회전
                      k : 반시계 방향 회전

스페이스바 : 정지 / q : 종료
-----------------------------------------
"""

class CheckerbotTeleop(Node):
    def __init__(self):
        super().__init__('checkerbot_teleop')
        
        # 퍼블리셔 설정 (Launch 파일의 브릿지 토픽과 일치시켜야 함)
        self.cmd_vel_pub = self.create_publisher(Twist, '/checkerbot/cmd_vel', 10)
        self.rail_pub = self.create_publisher(Float64, '/model/checkerboard_bot/joint/checkerbot/rail_joint/cmd_pos', 10)
        self.rotate_pub = self.create_publisher(Float64, '/model/checkerboard_bot/joint/checkerbot/checkerboard_joint/cmd_pos', 10)

        # 현재 상태 변수
        self.rail_pos = 0.0  # 초기 높이 (중간)
        self.rotate_angle = 0.0
        self.linear_vel = 0.3
        self.angular_vel = 0.5

    def publish_commands(self, key):
        twist = Twist()
        rail_msg = Float64()
        rotate_msg = Float64()

        if key == 'w': twist.linear.x = self.linear_vel
        elif key == 's': twist.linear.x = -self.linear_vel
        elif key == 'a': twist.angular.z = self.angular_vel
        elif key == 'd': twist.angular.z = -self.angular_vel
        
        # 상하 이동 제어 (Limit: 0.0 ~ 0.5) 
        elif key == 'u': self.rail_pos = min(self.rail_pos + 0.05, 0.5)
        elif key == 'j': self.rail_pos = max(self.rail_pos - 0.05, 0.0)
        
        # 회전 제어 
        elif key == 'i': self.rotate_angle += 0.05
        elif key == 'k': self.rotate_angle -= 0.05
        
        elif key == ' ': # 정지
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        # 메시지 발행
        self.cmd_vel_pub.publish(twist)
        rail_msg.data = self.rail_pos
        self.rail_pub.publish(rail_msg)
        rotate_msg.data = self.rotate_angle
        self.rotate_pub.publish(rotate_msg)

def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0.1)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, settings)
    return key

def main():
    settings = termios.tcgetattr(sys.stdin.fileno())
    rclpy.init()
    node = CheckerbotTeleop()
    print(msg)

    try:
        while True:
            key = get_key(settings)
            if key == 'q': break
            node.publish_commands(key)
    except Exception as e:
        print(e)
    finally:
        node.cmd_vel_pub.publish(Twist())
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()