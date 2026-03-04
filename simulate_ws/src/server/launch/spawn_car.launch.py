import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('server')

    # ==========================================
    # 1. Launch Arguments (외부에서 입력받을 변수들)
    # ==========================================
    car_name = LaunchConfiguration('car_name')
    x_pos = LaunchConfiguration('x_pos')
    y_pos = LaunchConfiguration('y_pos')
    z_pos = LaunchConfiguration('z_pos')

    declare_car_name = DeclareLaunchArgument('car_name', default_value='car1', description='car namespace')
    declare_x_pos = DeclareLaunchArgument('x_pos', default_value='0.8')
    declare_y_pos = DeclareLaunchArgument('y_pos', default_value='1.25')
    declare_z_pos = DeclareLaunchArgument('z_pos', default_value='0.3')
    # car2 spawn : x_pos=0.8, y_pos=-1.25, z_pos=0.3
    # ==========================================
    # 2. Xacro 파일 경로 설정
    # ==========================================
    xacro_path = os.path.join(pkg_share, 'urdf', 'car.xacro')

    # ==========================================
    # 3. Robot State Publisher 노드
    # ==========================================
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace=car_name,
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro ', xacro_path, ' car_name:=', car_name]),
            'frame_prefix': ''
        }]
    )
    # ==========================================
    # 4. Gazebo Sim 모델 생성 (새로운 방식 적용)
    # ==========================================
    # Gazebo 플러그인에게 스폰 명령을 내립니다.
    spawn_entity_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', car_name,
            '-topic', [car_name, '/robot_description'],
            '-x', x_pos,
            '-y', y_pos,
            '-z', z_pos
        
        ],
        output='screen'

    )

    # ==========================================
    # 5. ROS-Gazebo Bridge 노드 추가
    # ==========================================
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            ['/', car_name, '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'],
            ['/', car_name, '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry'],
            ['/', car_name, '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model'],
            ['/', car_name, '/scan/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked'],
            ['/', car_name, '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image'],
            ['/', car_name, '/gps/fix@sensor_msgs/msg/NavSatFix[gz.msgs.NavSat'],
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        output='screen'
    )
    return LaunchDescription([
        declare_car_name,
        declare_x_pos,
        declare_y_pos,
        declare_z_pos,
        robot_state_publisher_node,
        spawn_entity_node,
        bridge_node
    ])
