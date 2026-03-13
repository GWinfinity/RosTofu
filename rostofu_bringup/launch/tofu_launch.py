"""
Launch file for starting tofu ROS2 node.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for tofu node."""
    
    # Declare launch arguments
    tofu_path_arg = DeclareLaunchArgument(
        'tofu_path',
        default_value='',
        description='Path to tofu executable (auto-detected if empty)'
    )
    
    working_dir_arg = DeclareLaunchArgument(
        'working_directory',
        default_value='',
        description='Working directory for tofu process'
    )
    
    auto_start_arg = DeclareLaunchArgument(
        'auto_start',
        default_value='true',
        description='Automatically start tofu on node startup'
    )
    
    # Create the tofu node
    tofu_node = Node(
        package='rostofu_bringup',
        executable='tofu_node',
        name='tofu_node',
        output='screen',
        parameters=[{
            'tofu_path': LaunchConfiguration('tofu_path'),
            'working_directory': LaunchConfiguration('working_directory'),
            'auto_start': LaunchConfiguration('auto_start'),
        }],
        emulate_tty=True,
    )
    
    return LaunchDescription([
        tofu_path_arg,
        working_dir_arg,
        auto_start_arg,
        tofu_node,
    ])
