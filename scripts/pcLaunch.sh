#!/bin/bash

echo "🚀 Launching AEROTHON stack in separate Kitty windows..."

# 1. Gazebo Harmonic (Added NVIDIA Qt variables + interactive drop-in)
kitty --title "AEROTHON: Gazebo" distrobox enter ros -- bash -ic 'export QT_QPA_PLATFORM=xcb && export QT_X11_NO_MITSHM=1 && export GZ_SIM_SYSTEM_PLUGIN_PATH=$HOME/ardupilot_gazebo/build:${GZ_SIM_SYSTEM_PLUGIN_PATH} && export GZ_SIM_RESOURCE_PATH=$HOME/ardupilot_gazebo/models:${GZ_SIM_RESOURCE_PATH} && gz sim -v4 -r $HOME/ardupilot_gazebo/worlds/iris_runway.sdf; exec bash' &

# 2. ArduPilot SITL (Interactive drop-in)
kitty --title "AEROTHON: ArduPilot" distrobox enter ros -- bash -ic 'export PATH=$PATH:$HOME/ardupilot/Tools/autotest && source $HOME/venv-ardupilot/bin/activate && cd $HOME/ardupilot/ArduCopter && sim_vehicle.py -v ArduCopter -f JSON --console; exec bash' &

# 3. ROS 2 MAVROS Bridge (Interactive drop-in)
kitty --title "AEROTHON: MAVROS" distrobox enter ros -- bash -ic 'source /opt/ros/jazzy/setup.bash && ros2 launch mavros apm.launch fcu_url:=udp://127.0.0.1:14550@14555; exec bash' &

# 4. ROS-Gazebo Optic Nerve Camera (Interactive drop-in)
kitty --title "AEROTHON: Camera Bridge" distrobox enter ros -- bash -ic 'source /opt/ros/jazzy/setup.bash && ros2 run ros_gz_bridge parameter_bridge /world/iris_runway/model/iris_with_gimbal/model/gimbal/link/pitch_link/sensor/camera/image@sensor_msgs/msg/Image[gz.msgs.Image --ros-args -r /world/iris_runway/model/iris_with_gimbal/model/gimbal/link/pitch_link/sensor/camera/image:=/camera/image_raw; exec bash' &

echo "✅ All 4 subsystems have been launched in their own windows."
echo "You can close this terminal."
