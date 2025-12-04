from pyglm import glm
from .shape import Shape
import numpy as np

class Cube (Shape):

    def __init__ (self, color = glm.vec4(1.0), side_length = 1.0):
        self.side_length = side_length
        self.color = color
        super().__init__()

        
    def createGeometry(self):
        """
        Creates a unit cube by duplicating vertices to force normal per face
        """
        s = 0.5 * self.side_length

        # 24 vertices (4 per face)
        self.vertices = np.array([
            # front
            glm.vec4(-s, -s, s, 1.0), glm.vec4(s, -s, s, 1.0),
            glm.vec4(s, s, s, 1.0), glm.vec4(-s, s, s, 1.0),
            # back
            glm.vec4(-s, -s, -s, 1.0), glm.vec4(s, -s, -s, 1.0),
            glm.vec4(s, s, -s, 1.0), glm.vec4(-s, s, -s, 1.0),
            # top
            glm.vec4(-s, s, -s, 1.0), glm.vec4(s, s, -s, 1.0),
            glm.vec4(s, s, s, 1.0), glm.vec4(-s, s, s, 1.0),
            # bottom
            glm.vec4(-s, -s, -s, 1.0), glm.vec4(s, -s, -s, 1.0),
            glm.vec4(s, -s, s, 1.0), glm.vec4(-s, -s, s, 1.0),
            # right
            glm.vec4(s, -s, -s, 1.0), glm.vec4(s, s, -s, 1.0),
            glm.vec4(s, s, s, 1.0), glm.vec4(s, -s, s, 1.0),
            # left
            glm.vec4(-s, -s, -s, 1.0), glm.vec4(-s, s, -s, 1.0),
            glm.vec4(-s, s, s, 1.0), glm.vec4(-s, -s, s, 1.0),
        ], dtype=np.float32)

        # normals
        self.normals = np.array([
            *([glm.vec3(0, 0, 1)] * 4),  # front
            *([glm.vec3(0, 0, -1)] * 4),  # back
            *([glm.vec3(0, 1, 0)] * 4),  # top
            *([glm.vec3(0, -1, 0)] * 4),  # bottom
            *([glm.vec3(1, 0, 0)] * 4),  # right
            *([glm.vec3(-1, 0, 0)] * 4),  # left
        ], dtype=np.float32)

        # colors
        self.colors = np.full((len(self.vertices),4), self.color, dtype=np.float32)

        # UVs: each face gets a full [0,1] square
        face_uvs = [
            glm.vec2(0, 0), glm.vec2(1, 0),
            glm.vec2(1, 1), glm.vec2(0, 1)
        ]
        # UVs: adjust orientation per face so textures are not rotated
        self.uvs = np.array([
            glm.vec2(0, 0), glm.vec2(1, 0), glm.vec2(1, 1), glm.vec2(0, 1),
            glm.vec2(1, 0), glm.vec2(0, 0), glm.vec2(0, 1), glm.vec2(1, 1),
            glm.vec2(0, 1), glm.vec2(0, 0), glm.vec2(1, 0), glm.vec2(1, 1),
            glm.vec2(0, 0), glm.vec2(0, 1), glm.vec2(1, 1), glm.vec2(1, 0),
            glm.vec2(0, 0), glm.vec2(0, 1), glm.vec2(1, 1), glm.vec2(1, 0),
            glm.vec2(1, 0), glm.vec2(1, 1), glm.vec2(0, 1), glm.vec2(0, 0),
        ], dtype=np.float32)

        # indices
        self.indices = np.array([
            0, 1, 2, 0, 2, 3,  # front
            5, 4, 7, 5, 7, 6, # back
            9, 8, 11, 9, 11, 10,  # top
            12, 13, 14, 12, 14, 15,  # bottom
            16, 17, 18, 16, 18, 19,  # right
            21, 20, 23, 21, 23, 22 # left
        ], dtype=np.uint32)



