from pyglm import glm
from framework.shapes.shape import Shape
import numpy as np

class Grass(Shape):
    """
    A grass prism made of ONLY the 3 side faces (3 quads),
    with ALL normals pointing up (+Y) for grass-style lighting,
    and UVs mapped by real edge length to avoid warping.
    """

    def __init__(
        self,
        color=glm.vec4(1.0, 1.0, 1.0, 1.0),
        radius=0.35,
        height=0.8,
        tile_u=2.0,   # increase to repeat texture horizontally
        tile_v=1.0    # increase to repeat texture vertically
    ):
        self.color = color
        self.radius = float(radius)
        self.height = float(height)
        self.tile_u = float(tile_u)
        self.tile_v = float(tile_v)
        super().__init__()

    def createGeometry(self):
        r = self.radius
        h = self.height

        # Triangle base (XZ plane)
        A = glm.vec3(-r, 0.0, -r)
        B = glm.vec3( r, 0.0, -r)
        C = glm.vec3( 0.0, 0.0,  r)

        # Extruded top
        A1 = glm.vec3(A.x, h, A.z)
        B1 = glm.vec3(B.x, h, B.z)
        C1 = glm.vec3(C.x, h, C.z)

        verts, norms, cols, uvs, inds = [], [], [], [], []
        UP = glm.vec3(0.0, 1.0, 0.0)

        def xz_len(p, q) -> float:
            d = q - p
            return float(glm.length(glm.vec2(d.x, d.z)))

        def add_quad(p0, p1, p2, p3, u_len):
            base = len(verts)

            verts.extend([
                glm.vec4(p0, 1.0),
                glm.vec4(p1, 1.0),
                glm.vec4(p2, 1.0),
                glm.vec4(p3, 1.0),
            ])

            # Force upward normals
            norms.extend([UP, UP, UP, UP])
            cols.extend([self.color] * 4)

            # UVs: U follows real edge length (prevents warping), V follows height
            # Apply tiling factors to control repetition
            u = u_len * self.tile_u
            v = 1.0 * self.tile_v
            uvs.extend([
                glm.vec2(0.0, v),
                glm.vec2(u, v),
                glm.vec2(u, 0.0),
                glm.vec2(0.0, 0.0),
            ])

            inds.extend([
                base + 0, base + 1, base + 2,
                base + 0, base + 2, base + 3
            ])

        # 3 side faces only, with per-face UV length
        add_quad(A, B, B1, A1, u_len=xz_len(A, B))
        add_quad(B, C, C1, B1, u_len=xz_len(B, C))
        add_quad(C, A, A1, C1, u_len=xz_len(C, A))

        self.vertices = np.array(verts, dtype=np.float32)
        self.normals  = np.array(norms, dtype=np.float32)
        self.colors   = np.array(cols,  dtype=np.float32)
        self.uvs      = np.array(uvs,   dtype=np.float32)
        self.indices  = np.array(inds,  dtype=np.uint32)
