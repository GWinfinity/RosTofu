#!/usr/bin/env python3
"""
ROS2 Node for launching tofu application.
Compatible with both Windows and Linux/Ubuntu.
"""

import os
import sys
import subprocess
import signal
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from std_msgs.msg import String


class TofuNode(Node):
    """ROS2 Node that manages tofu process."""
    
    def __init__(self):
        super().__init__('tofu_node')
        
        # Declare parameters
        self.declare_parameter('tofu_path', '')
        self.declare_parameter('working_directory', '')
        self.declare_parameter('auto_start', True)
        
        # Get parameters
        tofu_path = self.get_parameter('tofu_path').value
        working_dir = self.get_parameter('working_directory').value
        auto_start = self.get_parameter('auto_start').value
        
        # Detect platform
        self.is_windows = sys.platform == 'win32'
        self.get_logger().info(f'Running on platform: {sys.platform}')
        
        # If not specified, try to find tofu executable
        if not tofu_path:
            tofu_path = self._find_tofu_executable()
        
        self.tofu_path = tofu_path
        self.working_dir = working_dir if working_dir else str(Path(tofu_path).parent) if tofu_path else os.getcwd()
        self.process = None
        
        # Create services
        self.start_service = self.create_service(Trigger, 'start_tofu', self.start_tofu_callback)
        self.stop_service = self.create_service(Trigger, 'stop_tofu', self.stop_tofu_callback)
        self.restart_service = self.create_service(Trigger, 'restart_tofu', self.restart_tofu_callback)
        
        # Create publisher for status
        self.status_publisher = self.create_publisher(String, 'tofu_status', 10)
        
        # Create timer for status check
        self.status_timer = self.create_timer(1.0, self.publish_status)
        
        # Auto start if enabled
        if auto_start and self.tofu_path:
            self.get_logger().info('Auto-starting tofu...')
            self.start_tofu()
        
        self.get_logger().info(f'TofuNode initialized')
        self.get_logger().info(f'Tofu path: {self.tofu_path}')
        self.get_logger().info(f'Working directory: {self.working_dir}')
    
    def _find_tofu_executable(self):
        """Auto-detect tofu executable path."""
        # Try common paths based on platform
        possible_paths = []
        
        if self.is_windows:
            possible_paths = [
                # Windows virtual environment paths
                Path(__file__).parent.parent.parent.parent / '.venv' / 'Scripts' / 'tofu.exe',
                Path(__file__).parent.parent.parent.parent / 'venv' / 'Scripts' / 'tofu.exe',
                Path.home() / 'RosTofu' / '.venv' / 'Scripts' / 'tofu.exe',
                Path('D:/githbi/RosTofu/.venv/Scripts/tofu.exe'),
            ]
        else:
            # Linux/Ubuntu paths
            possible_paths = [
                # Linux virtual environment paths
                Path(__file__).parent.parent.parent.parent / '.venv' / 'bin' / 'tofu',
                Path(__file__).parent.parent.parent.parent / 'venv' / 'bin' / 'tofu',
                Path.home() / 'RosTofu' / '.venv' / 'bin' / 'tofu',
                Path.home() / 'ros2_ws' / 'src' / 'RosTofu' / '.venv' / 'bin' / 'tofu',
                Path('/opt/rostofu/.venv/bin/tofu'),
            ]
            
            # Also try to find in PATH
            try:
                result = subprocess.run(['which', 'tofu'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except Exception:
                pass
        
        for path in possible_paths:
            if path.exists():
                self.get_logger().info(f'Auto-detected tofu at: {path}')
                return str(path)
        
        return ''
    
    def start_tofu(self):
        """Start the tofu process."""
        if self.process is not None and self.process.poll() is None:
            self.get_logger().warn('Tofu is already running')
            return False
        
        if not self.tofu_path or not os.path.exists(self.tofu_path):
            self.get_logger().error(f'Tofu executable not found: {self.tofu_path}')
            return False
        
        try:
            self.get_logger().info(f'Starting tofu: {self.tofu_path}')
            
            # Setup environment with virtual environment if available
            env = os.environ.copy()
            venv_path = Path(self.tofu_path).parent.parent
            if (venv_path / 'bin').exists() or (venv_path / 'Scripts').exists():
                # It's a virtual environment
                if self.is_windows:
                    env['PATH'] = str(venv_path / 'Scripts') + os.pathsep + env.get('PATH', '')
                else:
                    env['PATH'] = str(venv_path / 'bin') + os.pathsep + env.get('PATH', '')
                    env['VIRTUAL_ENV'] = str(venv_path)
            
            # Start tofu process with platform-specific settings
            if self.is_windows:
                # Windows: use CREATE_NEW_PROCESS_GROUP for proper termination
                self.process = subprocess.Popen(
                    [self.tofu_path],
                    cwd=self.working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                # Linux/Ubuntu: use start_new_session to create new process group
                self.process = subprocess.Popen(
                    [self.tofu_path],
                    cwd=self.working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    start_new_session=True,
                    preexec_fn=os.setsid if hasattr(os, 'setsid') else None
                )
            
            self.get_logger().info(f'Tofu started with PID: {self.process.pid}')
            return True
            
        except Exception as e:
            self.get_logger().error(f'Failed to start tofu: {e}')
            return False
    
    def stop_tofu(self):
        """Stop the tofu process."""
        if self.process is None:
            self.get_logger().warn('Tofu is not running')
            return False
        
        try:
            self.get_logger().info('Stopping tofu...')
            
            # Check if process is still running
            if self.process.poll() is not None:
                self.get_logger().info('Tofu has already stopped')
                self.process = None
                return True
            
            # Terminate the process
            if self.is_windows:
                # Windows: use taskkill to terminate the process tree
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
            else:
                # Linux: send SIGTERM to process group
                try:
                    pgid = os.getpgid(self.process.pid)
                    os.killpg(pgid, signal.SIGTERM)
                except ProcessLookupError:
                    # Process already gone
                    pass
                
                # Wait for graceful termination
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if not terminated
                    try:
                        pgid = os.getpgid(self.process.pid)
                        os.killpg(pgid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    self.process.kill()
            
            self.process = None
            self.get_logger().info('Tofu stopped successfully')
            return True
            
        except Exception as e:
            self.get_logger().error(f'Failed to stop tofu: {e}')
            return False
    
    def start_tofu_callback(self, request, response):
        """Service callback to start tofu."""
        success = self.start_tofu()
        response.success = success
        response.message = 'Tofu started successfully' if success else 'Failed to start tofu'
        return response
    
    def stop_tofu_callback(self, request, response):
        """Service callback to stop tofu."""
        success = self.stop_tofu()
        response.success = success
        response.message = 'Tofu stopped successfully' if success else 'Failed to stop tofu'
        return response
    
    def restart_tofu_callback(self, request, response):
        """Service callback to restart tofu."""
        self.stop_tofu()
        success = self.start_tofu()
        response.success = success
        response.message = 'Tofu restarted successfully' if success else 'Failed to restart tofu'
        return response
    
    def publish_status(self):
        """Publish tofu status."""
        msg = String()
        if self.process is None:
            msg.data = 'stopped'
        elif self.process.poll() is None:
            msg.data = 'running'
        else:
            msg.data = f'exited with code {self.process.returncode}'
            self.process = None
        self.status_publisher.publish(msg)
    
    def destroy_node(self):
        """Clean up when node is destroyed."""
        self.stop_tofu()
        super().destroy_node()


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)
    
    node = TofuNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard interrupt received, shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
