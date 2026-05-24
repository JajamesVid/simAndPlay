FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble

# Enable universe
RUN apt-get update && apt-get install -y software-properties-common \
 && add-apt-repository universe

# Basic tools + locale
RUN apt-get update && apt-get install -y \
    locales curl gnupg2 lsb-release wget git build-essential \
    && locale-gen en_US en_US.UTF-8

ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# -------------------------
# ROS 2 repository
# -------------------------
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc \
  | gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg

RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
  > /etc/apt/sources.list.d/ros2.list

# -------------------------
# Gazebo Fortress repository
# -------------------------
RUN curl -sSL https://packages.osrfoundation.org/gazebo.gpg \
  | gpg --dearmor -o /usr/share/keyrings/gazebo-archive-keyring.gpg

RUN echo "deb [signed-by=/usr/share/keyrings/gazebo-archive-keyring.gpg] \
  http://packages.osrfoundation.org/gazebo/ubuntu-stable \
  $(lsb_release -cs) main" \
  > /etc/apt/sources.list.d/gazebo-stable.list

# -------------------------
# Install everything
# -------------------------
RUN apt-get update && apt-get install -y \
    ros-humble-desktop \
    ros-humble-ros-gz \
    ros-humble-ros-gz-bridge \
    ros-humble-ros-gz-sim \
    gz-fortress \
    ros-humble-xacro \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-slam-toolbox \
    ros-humble-foxglove-bridge \
    python3-colcon-common-extensions \
    python3-vcstool \
    python3-pip \
    nano \
    # --- Display virtual (Xvfb + VNC + NoVNC) ---
    xvfb \
    x11vnc \
    novnc \
    websockify \
    # --- Qt / OpenGL dependencies ---
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libgles2-mesa-dev \
    libegl1-mesa \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxkbcommon-x11-0 \
    libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

# --- Python app dependencies ---
RUN pip3 install --no-cache-dir \
    PyQt6 \
    vispy \
    numpy \
    PyOpenGL

# Auto source ROS
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> /root/.bashrc

ENV IGN_IP=127.0.0.1

WORKDIR /workspace

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
