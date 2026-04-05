#!/bin/bash

echo "🚀 Launching AEROTHON stack in separate Kitty windows..."

# 1. Gazebo Harmonic
kitty --title "AEROTHON: Gazebo" --hold distrobox enter ros -- bash -c "cd ~ && export GZ_SIM_SYSTEM_PLUGIN_PATH=\$HOME/ardupilot_gazebo/build:\$GZ_SIM_SYSTEM_PLUGIN_PATH && export GZ_SIM_RESOURCE_PATH=\$HOME/ardupilot_gazebo/models:\$GZ_SIM_RESOURCE_PATH && gz sim -v4 -r ~/ardupilot_gazebo/worlds/iris_runway.sdf" &

# 2. ArduPilot SITL
kitty --title "AEROTHON: ArduPilot" --hold distrobox enter ros -- bash -c "cd ~/ardupilot/ArduCopter && sim_vehicle.py -v ArduCopter -f JSON --console" &

# 3. ROS 2 MAVROS Bridge
kitty --title "AEROTHON: MAVROS" --hold distrobox enter ros -- bash -c "cd ~ && source /opt/ros/jazzy/setup.bash && ros2 launch mavros apm.launch fcu_url:=udp://127.0.0.1:14550@14555" &

# 4. ROS-Gazebo Optic Nerve (Camera)
kitty --title "AEROTHON: Camera Bridge" --hold distrobox enter ros -- bash -c "cd ~ && source /opt/ros/jazzy/setup.bash && ros2 run ros_gz_bridge parameter_bridge /world/iris_runway/model/iris_with_gimbal/model/gimbal/link/pitch_link/sensor/camera/image@sensor_msgs/msg/Image[gz.msgs.Image --ros-args -r /world/iris_runway/model/iris_with_gimbal/model/gimbal/link/pitch_link/sensor/camera/image:=/camera/image_raw" &

echo "✅ All 4 subsystems have been launched in their own windows."
echo "You can close this terminal."
