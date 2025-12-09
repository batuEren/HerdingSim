import math
import random
import numpy as np
from pyglm import glm

from framework.shapes import Cylinder, Cone
from framework.shapes import Shape   # whatever your base is actually called


class TreeShape(Shape):
    """
    Single mesh containing trunk + foliage cones.
    """
    def __init__(self, height=4.0, width=4.0, segments=4,
                 cyl_segments=32, cone_segments=32):
        self.height = float(height)
        self.width = float(width)
        self.segments = int(segments)
        self.cyl_segments = int(cyl_segments)
        self.cone_segments = int(cone_segments)
        super().__init__()   # this should call createGeometry()

    def createGeometry(self):
        verts  = []
        norms  = []
        uvs    = []
        colors = []
        indices = []
        idx_offset = 0

        trunk_height   = self.height / 5.0
        foliage_height = self.height - trunk_height
        per_segment    = foliage_height / float(self.segments)

        # ---------- Helper for transforming a sub-mesh ----------
        def append_submesh(mesh, transform_mat):
            nonlocal idx_offset

            # positions
            for v in mesh.vertices:
                # v is [x, y, z, w], already with w=1
                p = glm.vec4(float(v[0]), float(v[1]), float(v[2]), float(v[3]))
                tp = transform_mat * p
                verts.append(tp)

            # normals (only translation, so we can keep them as-is)
            norms.extend(mesh.normals)

            # uvs, colors
            uvs.extend(mesh.uvs)
            colors.extend(mesh.colors)

            # indices with offset
            indices.extend((mesh.indices + idx_offset).tolist())
            idx_offset += mesh.vertices.shape[0]

        # ---------- Trunk ----------
        trunk_mesh = Cylinder(
            radius  = self.width / 4.0,
            height  = trunk_height,
            segments= self.cyl_segments,
            color   = glm.vec4(0.8, 0.5, 0.3, 1.0)
        )

        # place trunk so its base is at y=0
        trunk_transform = glm.translate(glm.vec3(0.0, trunk_height * 0.5, 0.0))
        append_submesh(trunk_mesh, trunk_transform)

        # ---------- Foliage cones ----------
        for i in range(self.segments):
            cone_height = per_segment
            cone_radius = self.width / max(1.0, math.log(i + 2))  # your formula

            color_rand = random.random()
            cone_color = glm.vec4(
                0.2 + 0.4 * color_rand,
                0.8 + 0.2 * color_rand,
                0.2 + 0.05 * color_rand,
                1.0
            )

            cone_mesh = Cone(
                radius  = cone_radius,
                height  = cone_height,
                segments= self.cone_segments,
                color   = cone_color
            )

            # same vertical placement logic as your original code
            cone_center_y = trunk_height + cone_height * 0.7 * (0.5 + i)
            cone_transform = glm.translate(glm.vec3(0.0, cone_center_y, 0.0))

            append_submesh(cone_mesh, cone_transform)

        # ---------- Convert to numpy arrays ----------
        self.vertices = np.array(
            [[v.x, v.y, v.z, v.w] for v in verts],
            dtype=np.float32
        )
        self.normals  = np.array(norms,  dtype=np.float32)
        self.uvs      = np.array(uvs,    dtype=np.float32)
        self.colors   = np.array(colors, dtype=np.float32)
        self.indices  = np.array(indices, dtype=np.uint32)
        self.vertices = trunk_mesh.vertices

