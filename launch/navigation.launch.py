import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('mobile_robot_urdf_description')
    nav2_pkg = get_package_share_directory('nav2_bringup')

    map_file = os.path.join(pkg, 'maps', 'my_world.yaml')
    params_file = os.path.join(pkg, 'config', 'nav2_params.yaml')
    rviz_config = os.path.join(nav2_pkg, 'rviz', 'nav2_default_view.rviz')

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_pkg, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': map_file,
            'params_file': params_file,
            'use_sim_time': 'true',
        }.items()
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([nav2, rviz])