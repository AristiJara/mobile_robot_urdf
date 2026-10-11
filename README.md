# mobile_robot_urdf

Differential-drive mobile robot with an **LD06 LiDAR** and a **BNO055 IMU**, simulated in **ROS 2 Humble + Gazebo Fortress**, with 2D mapping using **slam_toolbox**.

The robot structure was designed in CAD (Fusion 360) and exported to URDF/xacro. The off-the-shelf components (motors, motor driver, Raspberry Pi, ESP32 and wheels) were not designed by me; see [Design and credits](#design-and-credits). The project includes the full simulation: a world with walls and obstacles, sensors, differential drive controlled through `/cmd_vel`, odometry and SLAM.


## Features

- URDF/xacro model with STL meshes for visuals and simplified collisions (boxes, cylinders and spheres) to keep the simulation at real time (~100 %).
- Simulated 2D LiDAR (`gpu_lidar`, 360°, 10 Hz, 12 m range) and IMU (100 Hz).
- Differential drive using Gazebo's `DiffDrive` plugin, with velocity and acceleration limits matching **31 rpm** motors (≈ 0.11 m/s).
- ROS ↔ Gazebo bridge (`ros_gz_bridge`) configured through a YAML file.
- Custom 4×4 m world with walls, obstacles and a narrow corridor.
- Mapping with `slam_toolbox` and a saved map ready for localization/navigation.

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Fortress (`ign gazebo`)

```bash
sudo apt install \
  ros-humble-ros-gz \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-slam-toolbox \
  ros-humble-nav2-map-server \
  ros-humble-teleop-twist-keyboard
```

> On Humble, `ros-humble-ros-gz` uses Gazebo Fortress by default. Bridge message types are `ignition.msgs.*`.

## Installation

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone https://github.com/AristiJara/mobile_robot_urdf.git mobile_robot_urdf_description
cd ~/ros2_ws
colcon build --packages-select mobile_robot_urdf_description
source install/setup.bash
```

## Usage

Open one terminal per step and run `source ~/ros2_ws/install/setup.bash` in each one.

### 1. Simulation

```bash
ros2 launch mobile_robot_urdf_description gazebo.launch.py
```

Loads the world, publishes the robot description, spawns the robot in Gazebo (after 8 s) and starts the topic bridge.

### 2. SLAM

```bash
ros2 launch mobile_robot_urdf_description slam.launch.py
```

### 3. Drive the robot

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p speed:=0.1 -p turn:=0.4
```

Keys: `i` forward, `,` backward, `j`/`l` turn, `k` stop.

### 4. Visualize in RViz

```bash
rviz2 --ros-args -p use_sim_time:=true
```

- Fixed Frame: `map`
- Displays: **Map** (`/map`, Durability *Transient Local*), **LaserScan** (`/scan`, Reliability *Best Effort*), **RobotModel** (`/robot_description`).

### 5. Save the map

```bash
mkdir -p ~/ros2_ws/maps
ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/maps/my_map
```

This generates `my_map.pgm` and `my_map.yaml`. An example map (`world_1`) is included in `maps/`.

### Visualize the model only

```bash
ros2 launch mobile_robot_urdf_description display.launch.py
```

## Main topics

| Topic | Type | Direction |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | ROS → Gazebo |
| `/odom` | `nav_msgs/msg/Odometry` | Gazebo → ROS |
| `/scan` | `sensor_msgs/msg/LaserScan` | Gazebo → ROS |
| `/imu` | `sensor_msgs/msg/Imu` | Gazebo → ROS |
| `/joint_states` | `sensor_msgs/msg/JointState` | Gazebo → ROS |
| `/tf` | `tf2_msgs/msg/TFMessage` | Gazebo → ROS |
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo → ROS |
| `/map` | `nav_msgs/msg/OccupancyGrid` | slam_toolbox |

TF tree: `map → odom → base_link → {lidar_frame, imu_frame, ...}`

## Project structure

```
mobile_robot_urdf_description/
├── config/     # ros_gz_bridge_gazebo.yaml, slam_params.yaml, RViz configs
├── launch/     # display.launch.py, gazebo.launch.py, slam.launch.py
├── maps/       # saved maps (.pgm + .yaml)
├── meshes/     # robot STL meshes
├── urdf/       # xacro, materials, Gazebo plugins
├── worlds/     # empty_sensors.sdf (4x4 m room with obstacles)
├── package.xml
└── setup.py
```

## Technical notes

- **Simplified collisions.** Using the STL meshes as collision geometry dropped the real-time factor to 0.04 %. With primitive shapes and no `self_collide`, it went back to 100 %.
- **World systems.** The default empty world does not load the sensor or IMU systems; `empty_sensors.sdf` includes `ignition-gazebo-sensors-system` (ogre2) and `ignition-gazebo-imu-system`.
- **`DiffDrive` limits.** Without acceleration limits, the robot popped a wheelie when starting. Velocity (0.11 m/s) and acceleration (0.2 m/s²) were limited.
- **Map quality.** Fast turns degrade scan matching and produce overlapping maps. Turn slowly and drive along the perimeter before going around the obstacles.
- **RViz on Wayland.** If the Map display fails with a shader error, launch with `QT_QPA_PLATFORM=xcb rviz2 ...` or `LIBGL_ALWAYS_SOFTWARE=1 rviz2 ...`.
- `wheel_separation` (0.189 m) and `wheel_radius` (0.034 m) were estimated from the CAD model; adjust them if the model changes.

## Design and credits

**Designed by me (custom CAD):**

- Chassis plates (base, bottom mount, Raspberry mount, sensors mount)
- Motor brackets
- Threaded-rod standoff layout and overall assembly

**Commercial components (not my design):**

- DC gear motors (31 rpm)
- Motor driver
- Raspberry Pi 5 (with AI HAT)
- ESP32 board
- Wheels and caster wheel
- LD06 LiDAR and BNO055 IMU

### Third-party 3D models (not included)

The 3D models of the commercial components are **not included in this repository** because they are third-party work and I do not have permission to redistribute them. They are only used for visualization in the simulation. I converted them to STL/URDF with the Fusion 360 URDF exporter, but the geometry belongs to the original authors.

To get the full visual model, download each model from its source, export it as STL (scaled in millimeters, as the URDF uses `scale="0.001 0.001 0.001"`) and place it in `meshes/` with the file name listed below. Without them, RViz and Gazebo will show mesh errors for those links.

| Component | Mesh file(s) | Source |
|---|---|---|
| Adafruit BNO055 IMU | `imu_bno055_1.stl` | [GrabCAD](https://grabcad.com/library/adafruit-bno055-1) |
| JGB37-520 motor with quadrature encoder | `motor_left2_1.stl`, `motor_right2_1.stl` | [GrabCAD](https://grabcad.com/library/motor-jgb37-520-with-quadrature-encoder-1) |
| Raspberry Pi 5 | `raspberry_pi5_1.stl` | [GrabCAD](https://grabcad.com/library/raspberry-pi-5-2) |
| Raspberry Pi AI HAT | `ia_hat_1.stl` | [GrabCAD](https://grabcad.com/library/raspberry-pi-ai-hat-1) |
| LDRobot LD06 LiDAR | `lidar_ld06_1.stl` | [GrabCAD](https://grabcad.com/library/ldrobot-ld06-360-lidar-module-raspberry-pi-mounting-bracket-1) |
| ESP32 board, motor driver, wheels, caster wheel | `esp32_1.stl`, `motor_driver_1.stl`, `wheel_*_1.stl`, `caster_wheel_1.stl` | TODO: add source |

> Credit for these models goes to their original authors, listed on each GrabCAD page. The custom parts (chassis plates, brackets and standoffs) are included in `meshes/`.

## Target hardware

ESP32 (motor control), Raspberry Pi 5 (compute), LD06 LiDAR, BNO055 IMU and 31 rpm motors with 68 mm diameter wheels.

## Roadmap

- [ ] Localization with AMCL on the saved map
- [ ] Autonomous navigation with Nav2
- [ ] IMU and odometry fusion with `robot_localization` (EKF)
- [ ] Deployment on the real robot

## References

- [ROS 2 Humble documentation](https://docs.ros.org/en/humble/)
- [Gazebo Fortress documentation](https://gazebosim.org/docs/fortress)
- [ros_gz: ROS 2 ↔ Gazebo integration](https://github.com/gazebosim/ros_gz)
- [slam_toolbox](https://github.com/SteveMacenski/slam_toolbox)
- [Nav2](https://docs.nav2.org/) and [nav2_map_server](https://github.com/ros-navigation/navigation2/tree/humble/nav2_map_server)
- [fusion360-urdf-ros2 (Runtime Robotics)](https://github.com/runtimerobotics/fusion360-urdf-ros2): Fusion 360 to URDF exporter used to generate the base URDF
- [URDF specification](http://wiki.ros.org/urdf/XML)
- [REP 105: Coordinate frame conventions](https://www.ros.org/reps/rep-0105.html)
- [LD06 LiDAR datasheet (LDRobot)](https://www.ldrobot.com/)

## Author

[AristiJara](https://github.com/AristiJara)
