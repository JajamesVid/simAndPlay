"""
Parses a Gazebo SDF world file and extracts renderable geometry.
Returns a list of objects with type, size, pose, and color.
"""
import xml.etree.ElementTree as ET
import numpy as np


SKIP_MODELS = {'ground_plane'}


def _parse_pose(elem) -> list:
    """Returns [x, y, z, roll, pitch, yaw] from a <pose> element."""
    if elem is None:
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    return [float(v) for v in elem.text.strip().split()]


def _parse_vec3(text: str) -> list:
    return [float(v) for v in text.strip().split()]


def _parse_color(material_elem) -> tuple:
    """Returns (r, g, b, a) from a <material> element."""
    if material_elem is None:
        return (0.55, 0.55, 0.55, 1.0)
    for tag in ('ambient', 'diffuse'):
        el = material_elem.find(tag)
        if el is not None:
            parts = el.text.strip().split()
            return tuple(float(p) for p in parts[:4])
    return (0.55, 0.55, 0.55, 1.0)


def pose_to_matrix(pose: list) -> np.ndarray:
    """
    Converts SDF pose [x, y, z, roll, pitch, yaw] to a 4x4 transform matrix.
    Rotation order: Rz * Ry * Rx (extrinsic XYZ).
    """
    x, y, z, roll, pitch, yaw = pose

    cr, sr = np.cos(roll),  np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw),   np.sin(yaw)

    Rx = np.array([[1,  0,   0 ],
                   [0,  cr, -sr],
                   [0,  sr,  cr]])
    Ry = np.array([[ cp, 0, sp],
                   [  0, 1,  0],
                   [-sp, 0, cp]])
    Rz = np.array([[cy, -sy, 0],
                   [sy,  cy, 0],
                   [ 0,   0, 1]])

    R = Rz @ Ry @ Rx
    mat = np.eye(4, dtype=np.float32)
    mat[:3, :3] = R
    mat[3, :3]  = [x, y, z]   # Vispy uses row-major: translation in last row
    return mat


class SDFLoader:
    def parse(self, path: str) -> list:
        tree = ET.parse(path)
        root = tree.getroot()

        world = root.find('world') or root
        objects = []

        # Ground plane — render as a flat grey quad
        objects.append({
            'type':  'plane',
            'size':  [50.0, 50.0],
            'color': (0.25, 0.25, 0.25, 1.0),
        })

        for model in world.findall('model'):
            name = model.get('name', '')
            if name in SKIP_MODELS:
                continue

            model_pose = _parse_pose(model.find('pose'))

            for link in model.findall('link'):
                link_pose = _parse_pose(link.find('pose'))

                for visual in link.findall('visual'):
                    vis_pose = _parse_pose(visual.find('pose'))
                    color    = _parse_color(visual.find('material'))
                    geom     = visual.find('geometry')
                    if geom is None:
                        continue

                    # Combine model + link + visual poses (simple translation sum,
                    # rotation combination only for yaw which is common in flat worlds)
                    combined = [
                        model_pose[0] + link_pose[0] + vis_pose[0],
                        model_pose[1] + link_pose[1] + vis_pose[1],
                        model_pose[2] + link_pose[2] + vis_pose[2],
                        model_pose[3] + link_pose[3] + vis_pose[3],
                        model_pose[4] + link_pose[4] + vis_pose[4],
                        model_pose[5] + link_pose[5] + vis_pose[5],
                    ]

                    box = geom.find('box')
                    if box is not None:
                        size = _parse_vec3(box.find('size').text)
                        objects.append({
                            'type':   'box',
                            'name':   name,
                            'size':   size,
                            'pose':   combined,
                            'matrix': pose_to_matrix(combined),
                            'color':  color,
                        })
                        continue

                    sphere = geom.find('sphere')
                    if sphere is not None:
                        radius = float(sphere.find('radius').text)
                        objects.append({
                            'type':   'sphere',
                            'name':   name,
                            'radius': radius,
                            'pose':   combined,
                            'matrix': pose_to_matrix(combined),
                            'color':  color,
                        })
                        continue

                    cylinder = geom.find('cylinder')
                    if cylinder is not None:
                        radius = float(cylinder.find('radius').text)
                        length = float(cylinder.find('length').text)
                        objects.append({
                            'type':   'cylinder',
                            'name':   name,
                            'radius': radius,
                            'length': length,
                            'pose':   combined,
                            'matrix': pose_to_matrix(combined),
                            'color':  color,
                        })

        return objects
