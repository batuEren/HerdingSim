from pyglm import glm
from .shape import Shape
import numpy as np

class Triangle(Shape):

    def __init__(self, color=glm.vec4(1.0)):
        self.color = color
        super().__init__()

    def createGeometry(self):
        self.vertices = np.array([
            glm.vec4(-0.5, -0.5, 0.0, 1.0),  # bottom-left
            glm.vec4( 0.5, -0.5, 0.0, 1.0),  # bottom-right
            glm.vec4( 0.0,  0.5, 0.0, 1.0)   # top
        ], dtype=np.float32)

        self.normals = np.array([
            glm.vec3(0.0, 0.0, 1.0),
            glm.vec3(0.0, 0.0, 1.0),
            glm.vec3(0.0, 0.0, 1.0)
        ], dtype=np.float32)

        self.colors = np.array([
            self.color,
            self.color,
            self.color
        ], dtype=np.float32)

        self.uvs = np.array([
            glm.vec2(0.0, 0.0),  # bottom-left
            glm.vec2(1.0, 0.0),  # bottom-right
            glm.vec2(0.5, 1.0)   # top
        ], dtype=np.float32)

        self.indices = np.array([
            0, 2, 1
        ], dtype=np.uint32)
