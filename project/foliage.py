from pyglm import glm
from framework.shapes.shape import Shape
import numpy as np

class FoliageCard(Shape):
    """
    A single vertical quad (two triangles) centered at origin.
    Intended for instancing many times with different transforms.
    """
    def __init__(self, color=glm.vec4(1,1,1,1), width=0.6, height=0.9):
        self.color = color
        self.width = float(width)
        self.height = float(height)
        super().__init__()

    def createGeometry(self):
        w = self.width * 0.5
        h = self.height

        # vertical plane at Z=0, bottom at Y=0
        p0 = glm.vec3(-w, h, 0.0)  # top-left
        p1 = glm.vec3( w, h, 0.0)  # top-right
        p2 = glm.vec3( w, 0.0, 0.0)  # bottom-right
        p3 = glm.vec3(-w, 0.0, 0.0)  # bottom-left

        verts = [
            glm.vec4(p0, 1.0),
            glm.vec4(p1, 1.0),
            glm.vec4(p2, 1.0),
            glm.vec4(p3, 1.0),
        ]

        # cheap foliage lighting: “up” normals like your grass
        UP = glm.vec3(0.0, 0.0, 1.0)
        norms = [UP, UP, UP, UP]
        cols  = [self.color] * 4

        uvs = [
            glm.vec2(0.0, 1.0),
            glm.vec2(1.0, 1.0),
            glm.vec2(1.0, 0.0),
            glm.vec2(0.0, 0.0),
        ]

        inds = [0, 1, 2, 0, 2, 3]

        self.vertices = np.array(verts, dtype=np.float32)
        self.normals  = np.array(norms, dtype=np.float32)
        self.colors   = np.array(cols,  dtype=np.float32)
        self.uvs      = np.array(uvs,   dtype=np.float32)
        self.indices  = np.array(inds,  dtype=np.uint32)
