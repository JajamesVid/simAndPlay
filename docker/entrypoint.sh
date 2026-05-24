#!/bin/bash

# ── 1. Limpiar locks de X anteriores ─────────────────────────────────────────
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1 2>/dev/null || true

# ── 2. Virtual display (Xvfb) ────────────────────────────────────────────────
export DISPLAY=:1
Xvfb :1 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &

echo "Esperando Xvfb..."
for i in $(seq 1 20); do
    xdpyinfo -display :1 >/dev/null 2>&1 && break
    sleep 0.5
done

# ── 3. VNC + NoVNC ────────────────────────────────────────────────────────────
x11vnc -display :1 -nopw -listen 0.0.0.0 -rfbport 5900 -forever -shared -bg -q
sleep 0.5
websockify --web /usr/share/novnc 6080 localhost:5900 &

# ── 4. ROS workspace ──────────────────────────────────────────────────────────
source /opt/ros/humble/setup.bash

if [ ! -f /workspace/ros2_ws/install/setup.bash ]; then
    echo "Compilando workspace..."
    cd /workspace/ros2_ws
    colcon build --symlink-install
fi

source /workspace/ros2_ws/install/setup.bash

# ── 5. Lanzar simulación ──────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  simAndPlay arrancando...                    ║"
echo "║                                                              ║"
echo "║  Ver mundo 3D (Gazebo GUI):                                  ║"
echo "║  → http://localhost:6080/vnc.html                            ║"
echo "║                                                              ║"
echo "║  Ver topics ROS (Foxglove):                                  ║"
echo "║  → https://app.foxglove.dev  →  ws://localhost:8765          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

exec ros2 launch simandplay sim.launch.py
