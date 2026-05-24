"""
3D viewport — Vispy SceneCanvas embedded in a PyQt6 widget.
Renders the Gazebo world (boxes, spheres, cylinders) with an orbital camera.
"""
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from vispy import scene
from vispy.scene import visuals

from renderer.sdf_loader import SDFLoader


# ─────────────────────────────────────────────────────────────────────────────
# Mesh helpers (manual geometry so we control axes precisely)
# Coordinate system: X forward, Y left, Z up  (matches Gazebo / ROS)
# ─────────────────────────────────────────────────────────────────────────────

def _box_mesh(sx: float, sy: float, sz: float):
    """Unit box centered at origin with given half-extents."""
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    v = np.array([
        [-hx, -hy, -hz], [+hx, -hy, -hz], [+hx, +hy, -hz], [-hx, +hy, -hz],
        [-hx, -hy, +hz], [+hx, -hy, +hz], [+hx, +hy, +hz], [-hx, +hy, +hz],
    ], dtype=np.float32)
    f = np.array([
        [0, 1, 2], [0, 2, 3],   # bottom  (z-)
        [4, 6, 5], [4, 7, 6],   # top     (z+)
        [0, 1, 5], [0, 5, 4],   # front   (y-)
        [3, 2, 6], [3, 6, 7],   # back    (y+)
        [0, 3, 7], [0, 7, 4],   # left    (x-)
        [1, 2, 6], [1, 6, 5],   # right   (x+)
    ], dtype=np.uint32)
    return v, f


def _sphere_mesh(radius: float, rows: int = 16, cols: int = 24):
    verts, faces = [], []
    for i in range(rows + 1):
        theta = np.pi * i / rows
        for j in range(cols):
            phi = 2 * np.pi * j / cols
            x = radius * np.sin(theta) * np.cos(phi)
            y = radius * np.sin(theta) * np.sin(phi)
            z = radius * np.cos(theta)
            verts.append([x, y, z])
    for i in range(rows):
        for j in range(cols):
            a = i * cols + j
            b = i * cols + (j + 1) % cols
            c = (i + 1) * cols + j
            d = (i + 1) * cols + (j + 1) % cols
            faces += [[a, b, d], [a, d, c]]
    return np.array(verts, dtype=np.float32), np.array(faces, dtype=np.uint32)


def _cylinder_mesh(radius: float, length: float, segs: int = 24):
    verts, faces = [], []
    half = length / 2
    # Side vertices
    for i in range(segs):
        angle = 2 * np.pi * i / segs
        x, y = radius * np.cos(angle), radius * np.sin(angle)
        verts += [[x, y, -half], [x, y, +half]]
    # Side faces
    for i in range(segs):
        a, b = 2 * i, 2 * i + 1
        c, d = 2 * ((i + 1) % segs), 2 * ((i + 1) % segs) + 1
        faces += [[a, c, d], [a, d, b]]
    # Cap centers
    bot, top = len(verts), len(verts) + 1
    verts += [[0, 0, -half], [0, 0, +half]]
    for i in range(segs):
        a = 2 * i
        c = 2 * ((i + 1) % segs)
        faces += [[bot, c, a], [top, a + 1, c + 1]]
    return np.array(verts, dtype=np.float32), np.array(faces, dtype=np.uint32)


def _ground_mesh(size: float = 50.0):
    h = size / 2
    v = np.array([[-h, -h, 0], [+h, -h, 0], [+h, +h, 0], [-h, +h, 0]], dtype=np.float32)
    f = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32)
    return v, f


# ─────────────────────────────────────────────────────────────────────────────

class Viewport3D(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ── Vispy canvas ──────────────────────────────────────────────────────
        self.canvas = scene.SceneCanvas(
            keys='interactive',
            bgcolor='#0d1117',
            show=False,
        )
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.cameras.TurntableCamera(
            elevation=30,
            azimuth=45,
            distance=18,
            up='+z',
            fov=45,
        )

        self._build_static_scene()

        # ── Embed in Qt ───────────────────────────────────────────────────────
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas.native)

        self._objects = []   # vispy visuals currently in scene

    # ── Static scene elements ─────────────────────────────────────────────────

    def _build_static_scene(self):
        # Ground grid
        self._grid = visuals.GridLines(color=(0.2, 0.6, 0.2, 0.4), parent=self.view.scene)

        # XYZ axis (small, in scene origin)
        self._axis = visuals.XYZAxis(parent=self.view.scene)

        # Subtle ambient grid text hint
        self._ground_mesh = self._add_mesh(
            *_ground_mesh(50.0),
            color=(0.12, 0.14, 0.16, 1.0),
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def load_sdf(self, path: str):
        self.clear_world()
        loader = SDFLoader()
        objects = loader.parse(path)
        for obj in objects:
            self._add_object(obj)
        self.canvas.update()

    def clear_world(self):
        for vis in self._objects:
            vis.parent = None
        self._objects.clear()

    def reset_camera(self):
        self.view.camera.set_state({
            'elevation': 30, 'azimuth': 45, 'distance': 18,
        })
        self.canvas.update()

    # ── Internal rendering ────────────────────────────────────────────────────

    def _add_object(self, obj: dict):
        t = obj.get('type')
        color = obj.get('color', (0.6, 0.6, 0.6, 1.0))
        matrix = obj.get('matrix')

        if t == 'plane':
            vis = self._add_mesh(*_ground_mesh(obj['size'][0]), color=color)
        elif t == 'box':
            s = obj['size']
            vis = self._add_mesh(*_box_mesh(s[0], s[1], s[2]), color=color, matrix=matrix)
        elif t == 'sphere':
            vis = self._add_mesh(*_sphere_mesh(obj['radius']), color=color, matrix=matrix)
        elif t == 'cylinder':
            vis = self._add_mesh(
                *_cylinder_mesh(obj['radius'], obj['length']),
                color=color, matrix=matrix,
            )
        else:
            return

        self._objects.append(vis)

    def _add_mesh(self, vertices, faces, color, matrix=None) -> visuals.Mesh:
        # Solid face
        mesh = visuals.Mesh(
            vertices=vertices,
            faces=faces,
            color=color,
            shading='flat',
            parent=self.view.scene,
        )
        # Wireframe overlay (subtle edge lines)
        wire = visuals.Mesh(
            vertices=vertices,
            faces=faces,
            color=(1, 1, 1, 0.06),
            mode='lines',
            parent=self.view.scene,
        )

        if matrix is not None:
            t = scene.transforms.MatrixTransform()
            t.matrix = matrix
            mesh.transform = t
            wire.transform = t

        self._objects.append(wire)
        return mesh
