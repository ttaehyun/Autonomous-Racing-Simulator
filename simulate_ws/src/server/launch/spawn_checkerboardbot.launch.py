import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    # 패키지명 'server'
    pkg_share = get_package_share_directory('server')

    # ==========================================
    # 1. Launch Arguments
    # ==========================================
    bot_name = LaunchConfiguration('bot_name')
    x_pos = LaunchConfiguration('x_pos')
    y_pos = LaunchConfiguration('y_pos')
    z_pos = LaunchConfiguration('z_pos')
    yaw_pos = LaunchConfiguration('yaw')
    # Gazebo에 생성될 모델 이름 (xacro의 name 속성과 일치시키는 것이 좋습니다)
    declare_bot_name = DeclareLaunchArgument('bot_name', default_value='checkerboard_bot')
    declare_x_pos = DeclareLaunchArgument('x_pos', default_value='3.0')
    declare_y_pos = DeclareLaunchArgument('y_pos', default_value='1.25')
    declare_z_pos = DeclareLaunchArgument('z_pos', default_value='0.5')
    declare_yaw_pos = DeclareLaunchArgument('yaw', default_value='3.14159')
    xacro_path = os.path.join(pkg_share, 'urdf', 'checkerboard.xacro')

    # ==========================================
    # 2. Robot State Publisher 노드
    # ==========================================
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace='checkerbot',  # ROS 토픽들의 네임스페이스를 checkerbot으로 묶음
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro ', xacro_path]),
            'use_sim_time': True
        }]
    )

    # ==========================================
    # 3. Gazebo Sim 모델 생성
    # ==========================================
    spawn_entity_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', bot_name,
            # namespace가 checkerbot이므로 robot_description 토픽 경로도 맞춰줍니다.
            '-topic', '/checkerbot/robot_description',
            '-x', x_pos,
            '-y', y_pos,
            '-z', z_pos,
            '-Y', yaw_pos
        ],
        output='screen'
    )

    # ==========================================
    # 4. ROS-Gazebo Bridge 노드 (핵심)
    # ==========================================
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='checkerbot_bridge',
        arguments=[
            # 1) 주행 및 오도메트리 (수정한 네임스페이스 반영)
            '/checkerbot/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/checkerbot/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            
            # 2) 조인트 상태
            '/checkerbot/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            
            # 3) 체커보드 제어 (Xacro에 작성된 <topic> 태그 경로와 정확히 일치)
            '/model/checkerboard_bot/joint/checkerbot/rail_joint/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double',
            '/model/checkerboard_bot/joint/checkerbot/checkerboard_joint/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double',
            
            # 4) TF 및 Clock (Gazebo의 TF를 ROS의 글로벌 /tf로 보내되, 충돌 없도록 리매핑)
            '/model/checkerboard_bot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        remappings=[
            ('/model/checkerboard_bot/tf', '/tf')
        ],
        output='screen'
    )

    return LaunchDescription([
        declare_bot_name,
        declare_x_pos,
        declare_y_pos,
        declare_z_pos,
        declare_yaw_pos,
        robot_state_publisher_node,
        spawn_entity_node,
        bridge_node
    ])