from pyglm import glm
from .shape import Shape
import numpy as np

class Quad(Shape):
    def __init__(self, color=glm.vec4(1.0), width=1.0, height=1.0):
        self.width = width
        self.height = height
        self.color = color
        super().__init__()

    def createGeometry(self):
        """
        Creates a simple quad in the XY plane, centered at the origin.
        """
        hw = 0.5 * self.width
        hh = 0.5 * self.height

        # 4 vertices
        self.vertices = np.array([
            glm.vec4(-hw, -hh, 0.0, 1.0),  # bottom-left
            glm.vec4(hw, -hh, 0.0, 1.0),   # bottom-right
            glm.vec4(hw, hh, 0.0, 1.0),    # top-right
            glm.vec4(-hw, hh, 0.0, 1.0),   # top-left
        ], dtype=np.float32)

        # normals (all facing +Z)
        self.normals = np.array([
            glm.vec3(0, 0, 1),
            glm.vec3(0, 0, 1),
            glm.vec3(0, 0, 1),
            glm.vec3(0, 0, 1),
        ], dtype=np.float32)

        # colors
        self.colors = np.full((4, 4), self.color, dtype=np.float32)

        # UVs
        self.uvs = np.array([
            glm.vec2(0, 0),
            glm.vec2(1, 0),
            glm.vec2(1, 1),
            glm.vec2(0, 1),
        ], dtype=np.float32)

        # indices (two triangles)
        self.indices = np.array([
            0, 1, 2,
            0, 2, 3
        ], dtype=np.uint32)
