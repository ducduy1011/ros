import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_share = get_package_share_directory('my_robot_description')
    pkg_tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    world_path = os.path.join(pkg_tb3_gazebo, 'worlds', 'turtlebot3_world.world')
    workspace_models_path = os.path.join(pkg_share, '..')

    urdf_file = os.path.join(pkg_share, 'urdf', 'Assem1_4.urdf')
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'sim.rviz')
    with open(urdf_file, 'r', encoding='utf-8') as f:
        robot_desc = f.read()

    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=[
            os.environ.get('GAZEBO_MODEL_PATH', ''), 
            ':', workspace_models_path,
            ':', os.path.join(pkg_tb3_gazebo, 'models')
        ]
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        parameters=[{'use_sim_time': True}]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_path}.items()
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-file', urdf_file,
            '-entity', 'my_robot',
            '-x', '-2.0', '-y', '-0.5', '-z', '0.01'
        ],
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        set_gazebo_model_path,
        robot_state_publisher,
        joint_state_publisher,
        gazebo,
        spawn_entity,
        rviz_node
    ])