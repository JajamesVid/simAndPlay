import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    pkg = get_package_share_directory('simandplay')

    urdf_file = os.path.join(pkg, 'urdf', 'robot.urdf.xacro')
    robot_description = xacro.process_file(urdf_file).toxml()

    world_file = os.path.join(pkg, 'worlds', 'simple_room.sdf')
    sdf_file = os.path.join(pkg, 'models', 'robot.sdf')

    # 1. Gazebo server (headless, sin GUI)
    gazebo_server = ExecuteProcess(
        cmd=['ign', 'gazebo', '-s', '-r', world_file],
        output='screen',
        additional_env={'IGN_GAZEBO_RESOURCE_PATH': pkg}
    )

    # 2. Gazebo GUI (conecta al servidor via Ignition transport)
    gazebo_gui = ExecuteProcess(
        cmd=['ign', 'gazebo', '-g'],
        output='screen',
    )

    # 3. Spawn robot desde SDF
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'robot',
            '-file', sdf_file,
            '-x', '0', '-y', '0', '-z', '0.0',
        ],
        output='screen'
    )

    # 4. Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }]
    )

    # 5. ROS-Gazebo bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/camera/image@sensor_msgs/msg/Image[ignition.msgs.Image',
        ],
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    # 6. Foxglove bridge
    foxglove = Node(
        package='foxglove_bridge',
        executable='foxglove_bridge',
        name='foxglove_bridge',
        parameters=[{
            'port': 8765,
            'address': '0.0.0.0',
            'tls': False,
            'use_sim_time': True,
        }],
        output='screen'
    )

    delayed_gui    = TimerAction(period=2.0, actions=[gazebo_gui])
    delayed_spawn  = TimerAction(period=4.0, actions=[spawn_robot])
    delayed_bridge = TimerAction(period=5.0, actions=[bridge])

    return LaunchDescription([
        gazebo_server,
        robot_state_publisher,
        delayed_gui,
        delayed_spawn,
        delayed_bridge,
        foxglove,
    ])
