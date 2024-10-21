from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
import os

dev_name = os.getenv('DEV_NAME')  # user_thesis
ws_name = os.getenv('WS_NAME')    # docker_ws

def generate_launch_description():
    nodes = [
            # PX4 <-> ROS2 bridge
            ExecuteProcess(name="MicroXRCEAgent", cmd=["MicroXRCEAgent", "udp4", "-p", "8888"], shell=True),

            #Forward topic di Gazebo su topic ROS2 per velocità motori
            Node(package="ros_gz_bridge", executable="parameter_bridge", name="BridgeGZTopicToRos", arguments=[
                    '/x500_0/command/motor_speed@actuator_msgs/msg/Actuators[gz.msgs.Actuators'
            ]),

            # PX4 simulator + Gazebo
            ExecuteProcess(
                name="PX4",
                cmd=["make", "-C", os.path.join('/home', os.getenv('DEV_NAME'), 'PX4-Autopilot'), "HEADLESS=1", "px4_sitl", "gz_x500"], prefix="gnome-terminal --", shell=True
            ),
        
            # WebSocket server su porta 9090
            Node(package="rosbridge_server", executable="rosbridge_websocket", name="rosbridge"),

            # Terminale di controllo
            Node(package="px4_offboard", executable="control", prefix="gnome-terminal --", name="gnome_controller"),
            
            # Bridge tra /fmu e il terminale di controllo
            Node(package="px4_offboard", executable="velocity_control", name="velocity_controller"),

            # Bridge tra /fmu e /px4_visualizer. Traduce i messaggi da PX4 a ROS2
            Node(package="px4_offboard", executable="visualizer"),

            # RVIZ2 Visualizer
            Node(package="rviz2", executable="rviz2", arguments=[
                '-d', [os.path.join('/home', dev_name, ws_name, 'ros2_px4_quadcopter_controller_ws', 'src', 'ROS2_PX4_Quadcopter_Controller', 'px4_offboard', 'resource', 'visualize.rviz')]
            ]),

            # Grafo di nodi e topic
            ExecuteProcess(cmd=["rqt_graph"]),
    ]

    return LaunchDescription(nodes)
