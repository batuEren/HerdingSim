from pyglm import glm
from .shape import Shape
import numpy as np
import math

class Cone(Shape):
    """
    Cone aligned along Y axis, centered at origin.
    Parameters:
        radius: base radius
        height: height
        segments: number of vertices around the base
        split_faces: if True, duplicate vertices per face (flat shading, clean UVs).
                     if False, share vertices (smooth shading, continuous UVs).
    """
    def __init__(self, radius=0.5, height=1.0, segments=32,
                 color=glm.vec4(1.0), split_faces=False):
        self.radius = radius
        self.height = height
        self.segments = segments
        self.color = color
        self.split_faces = split_faces
        super().__init__()

    def createGeometry(self):
        verts, norms, uvs, indices = [], [], [], []

        y_top = 0.5 * self.height
        y_bot = -0.5 * self.height

        if self.split_faces:
            # --- Side faces: duplicate vertices per triangle ---
            for i in range(self.segments):
                theta1 = 2 * math.pi * i / self.segments
                theta2 = 2 * math.pi * (i+1) / self.segments

                # Apex
                apex = glm.vec4(0, y_top, 0, 1.0)
                verts.append(apex)
                norms.append(glm.normalize(glm.vec3(
                    math.cos((theta1+theta2)/2),
                    self.radius/self.height,
                    math.sin((theta1+theta2)/2)
                )))
                uvs.append(glm.vec2((theta1+theta2)/(2*math.pi), 1.0))

                # Base ring vertex 1
                x1, z1 = self.radius*math.cos(theta1), self.radius*math.sin(theta1)
                verts.append(glm.vec4(x1, y_bot, z1, 1.0))
                norms.append(glm.normalize(glm.vec3(x1, self.radius/self.height, z1)))
                uvs.append(glm.vec2(i/self.segments, 0.0))

                # Base ring vertex 2
                x2, z2 = self.radius*math.cos(theta2), self.radius*math.sin(theta2)
                verts.append(glm.vec4(x2, y_bot, z2, 1.0))
                norms.append(glm.normalize(glm.vec3(x2, self.radius/self.height, z2)))
                uvs.append(glm.vec2((i+1)/self.segments, 0.0))

                base = len(verts) - 3
                indices += [base, base+1, base+2]

            # --- Base disk: duplicate per triangle ---
            center = glm.vec4(0, y_bot, 0, 1.0)
            for i in range(self.segments):
                theta1 = 2 * math.pi * i / self.segments
                theta2 = 2 * math.pi * (i+1) / self.segments

                # Center
                verts.append(center)
                norms.append(glm.vec3(0,-1,0))
                uvs.append(glm.vec2(0.5,0.5))

                # Rim 1
                x1, z1 = self.radius*math.cos(theta1), self.radius*math.sin(theta1)
                verts.append(glm.vec4(x1, y_bot, z1, 1.0))
                norms.append(glm.vec3(0,-1,0))
                uvs.append(glm.vec2(0.5+0.5*math.cos(theta1), 0.5+0.5*math.sin(theta1)))

                # Rim 2
                x2, z2 = self.radius*math.cos(theta2), self.radius*math.sin(theta2)
                verts.append(glm.vec4(x2, y_bot, z2, 1.0))
                norms.append(glm.vec3(0,-1,0))
                uvs.append(glm.vec2(0.5+0.5*math.cos(theta2), 0.5+0.5*math.sin(theta2)))

                base = len(verts) - 3
                indices += [base, base+2, base+1]

        else:
            # --- Shared vertices version (smooth shading) ---
            apex = glm.vec4(0, y_top, 0, 1.0)
            verts.append(apex)
            norms.append(glm.vec3(0,1,0))
            uvs.append(glm.vec2(0.5,1.0))
            apex_index = 0

            # Base ring for sides
            for i in range(self.segments):
                theta = 2*math.pi*i/self.segments
                x = self.radius*math.cos(theta)
                z = self.radius*math.sin(theta)
                verts.append(glm.vec4(x,y_bot,z,1.0))
                side_normal = glm.normalize(glm.vec3(x, self.radius/self.height, z))
                norms.append(side_normal)
                uvs.append(glm.vec2(i/self.segments, 0.0))

            for i in range(self.segments):
                i1 = 1+i
                i2 = 1+((i+1)%self.segments)
                indices += [apex_index,i1,i2]

            # Base center
            base_center_index = len(verts)
            verts.append(glm.vec4(0,y_bot,0,1.0))
            norms.append(glm.vec3(0,-1,0))
            uvs.append(glm.vec2(0.5,0.5))

            for i in range(self.segments):
                theta = 2*math.pi*i/self.segments
                x = self.radius*math.cos(theta)
                z = self.radius*math.sin(theta)
                verts.append(glm.vec4(x,y_bot,z,1.0))
                norms.append(glm.vec3(0,-1,0))
                uvs.append(glm.vec2(0.5+0.5*math.cos(theta), 0.5+0.5*math.sin(theta)))

            for i in range(self.segments):
                i1 = base_center_index+1+i
                i2 = base_center_index+1+((i+1)%self.segments)
                indices += [base_center_index,i2,i1]

        # Convert to numpy arrays
        self.vertices = np.array(verts, dtype=np.float32)
        self.normals  = np.array(norms, dtype=np.float32)
        self.colors   = np.full((len(verts),4), self.color, dtype=np.float32)
        self.uvs      = np.array(uvs, dtype=np.float32)
        self.indices  = np.array(indices, dtype=np.uint32)
