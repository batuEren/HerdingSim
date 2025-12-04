from pyglm import glm
from .shape import Shape
import numpy as np
import math

class UVSphere(Shape):
    """
    UV sphere centered at origin.
    Parameters:
        radius: sphere radius
        stacks: vertical resolution
        slices: horizontal resolution
        split_faces: if True, duplicate vertices per quad (flat shading, clean UVs)
    """
    def __init__(self, radius=0.5, stacks=16, slices=32,
                 color=glm.vec4(1.0), split_faces=False):
        self.radius = radius
        self.stacks = stacks
        self.slices = slices
        self.split_faces = split_faces
        self.color = color
        super().__init__()

    def createGeometry(self):
        verts, norms, uvs, indices = [], [], [], []

        if self.split_faces:
            # Duplicate vertices per quad
            for i in range(self.stacks):
                phi1 = math.pi * i / self.stacks
                phi2 = math.pi * (i+1) / self.stacks
                for j in range(self.slices):
                    theta1 = 2*math.pi * j / self.slices
                    theta2 = 2*math.pi * (j+1) / self.slices

                    # four corners of the quad
                    quad = [
                        (phi1, theta1),
                        (phi2, theta1),
                        (phi1, theta2),
                        (phi2, theta2)
                    ]
                    base = len(verts)
                    for phi, theta in quad:
                        x = self.radius * math.sin(phi) * math.cos(theta)
                        y = self.radius * math.cos(phi)
                        z = self.radius * math.sin(phi) * math.sin(theta)
                        verts.append(glm.vec4(x,y,z,1.0))
                        norms.append(glm.normalize(glm.vec3(x,y,z)))
                        u = theta / (2*math.pi)
                        v = phi / math.pi
                        uvs.append(glm.vec2(u,v))
                    # two triangles
                    indices += [base, base+1, base+2, base+2, base+1, base+3]

        else:
            # Shared vertices version
            for i in range(self.stacks+1):
                phi = math.pi*i/self.stacks
                y = self.radius*math.cos(phi)
                r = self.radius*math.sin(phi)
                for j in range(self.slices+1):
                    theta = 2*math.pi*j/self.slices
                    x = r*math.cos(theta)
                    z = r*math.sin(theta)
                    verts.append(glm.vec4(x,y,z,1.0))
                    norms.append(glm.normalize(glm.vec3(x,y,z)))
                    u = j/self.slices
                    v = i/self.stacks
                    uvs.append(glm.vec2(u,v))

            for i in range(self.stacks):
                for j in range(self.slices):
                    i0 = i*(self.slices+1)+j
                    i1 = i0+1
                    i2 = i0+(self.slices+1)
                    i3 = i2+1
                    indices += [i0,i2,i1, i1,i2,i3]

        self.vertices = np.array(verts,dtype=np.float32)
        self.normals  = np.array(norms,dtype=np.float32)
        self.colors   = np.full((len(verts),4), self.color, dtype=np.float32)
        self.uvs      = np.array(uvs,dtype=np.float32)
        self.indices  = np.array(indices,dtype=np.uint32)
