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
    python3-colcon-common-extensions \
    python3-vcstool \
    python3-pip \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Auto source ROS
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> /root/.bashrc

WORKDIR /workspace

CMD ["/bin/bash"]