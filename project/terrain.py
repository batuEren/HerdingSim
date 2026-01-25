# terrain.py
import math
import random
import numpy as np
from pyglm import glm
from framework.shapes import Shape


def default_height_func(x, z):
    #default height
    return (
        0.7 * math.sin(0.15 * x) * math.cos(0.15 * z) +
        0.3 * math.sin(0.05 * (x + z))
    )

_RANDOM_HEIGHT_PARAMS = None

def init_random_height_params(seed=None):
    global _RANDOM_HEIGHT_PARAMS
    rng = random.Random(seed) if seed is not None else random
    _RANDOM_HEIGHT_PARAMS = {
        "a1": rng.uniform(2.0, 3.2),
        "f1x": rng.uniform(0.03, 0.08),
        "f1z": rng.uniform(0.015, 0.05),
        "a2": rng.uniform(1.8, 2.8),
        "f2": rng.uniform(0.015, 0.04),
    }
    return _RANDOM_HEIGHT_PARAMS

def random_height_func(x, z):
    # Initialize once per program run.
    if _RANDOM_HEIGHT_PARAMS is None:
        init_random_height_params()
    p = _RANDOM_HEIGHT_PARAMS
    return (
        p["a1"] * math.sin(p["f1x"] * x) * math.cos(p["f1z"] * z) +
        p["a2"] * math.sin(p["f2"] * (x + z))
    )


class Terrain(Shape):
    def __init__(self,
                 width=100.0,
                 depth=100.0,
                 res_x=200,
                 res_z=200,
                 color=glm.vec4(0.2, 0.8, 0.3, 1.0),
                 height_func=random_height_func):
        """
        width, depth : world size along X and Z
        res_x, res_z : number of quads along X and Z
                       (vertices are (res_x+1) x (res_z+1))
        color        : base vertex color
        height_func  : function (x, z) -> y
        """
        self.width = width
        self.depth = depth
        self.res_x = res_x
        self.res_z = res_z
        self.color = color
        self.height_func = height_func

        super().__init__()  # calls createGeometry()


    def createGeometry(self):
        num_verts_x = self.res_x + 1
        num_verts_z = self.res_z + 1

        dx = self.width / float(self.res_x)
        dz = self.depth / float(self.res_z)

        # Center terrain around origin
        x0 = -0.5 * self.width
        z0 = -0.5 * self.depth

        vertices = []
        normals_accum = [glm.vec3(0.0, 0.0, 0.0)
                         for _ in range(num_verts_x * num_verts_z)]
        uvs = []
        colors = []
        indices = []

        def idx(i, j):
            return j * num_verts_x + i

        for j in range(num_verts_z):
            z = z0 + j * dz
            v = j / float(self.res_z)

            for i in range(num_verts_x):
                x = x0 + i * dx
                u = i / float(self.res_x)

                y = self.height_func(x, z)

                vertices.append(glm.vec4(x, y, z, 1.0))
                uvs.append(glm.vec2(u, v))
                colors.append(self.color)

        # 2 triangles per quad
        for j in range(self.res_z):
            for i in range(self.res_x):
                i0 = idx(i,     j)
                i1 = idx(i + 1, j)
                i2 = idx(i,     j + 1)
                i3 = idx(i + 1, j + 1)

                # Triangle 1: i0, i2, i1
                indices.extend([i0, i2, i1])
                # Triangle 2: i1, i2, i3
                indices.extend([i1, i2, i3])

        # accumulate triangle normals for smooth shading
        for t in range(0, len(indices), 3):
            ia = indices[t]
            ib = indices[t + 1]
            ic = indices[t + 2]

            p0 = glm.vec3(vertices[ia].x, vertices[ia].y, vertices[ia].z)
            p1 = glm.vec3(vertices[ib].x, vertices[ib].y, vertices[ib].z)
            p2 = glm.vec3(vertices[ic].x, vertices[ic].y, vertices[ic].z)

            e1 = p1 - p0
            e2 = p2 - p0
            n = glm.normalize(glm.cross(e1, e2))

            normals_accum[ia] += n
            normals_accum[ib] += n
            normals_accum[ic] += n

        # normalize per-vertex normals
        normals = [glm.normalize(n) for n in normals_accum]

        # convert to numpy arrays for the renderer
        self.vertices = np.array(vertices, dtype=np.float32)
        self.normals  = np.array(normals,  dtype=np.float32)
        self.colors   = np.array(colors,   dtype=np.float32)
        self.uvs      = np.array(uvs,      dtype=np.float32)
        self.indices  = np.array(indices,  dtype=np.uint32)
