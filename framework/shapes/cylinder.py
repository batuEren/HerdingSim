from pyglm import glm
from .shape import Shape
import numpy as np
import math

class Cylinder(Shape):
    """
    Cylinder aligned along Y axis, centered at origin.
    Parameters:
        radius: radius of the cylinder
        height: height of the cylinder
        segments: number of vertices around the ring
        split_faces: if True, duplicate vertices per face (flat shading, clean UVs)
    """
    def __init__(self, radius=0.5, height=1.0, segments=32,
                 color=glm.vec4(1.0), split_faces=False):
        self.radius = radius
        self.height = height
        self.segments = segments
        self.split_faces = split_faces
        self.color = color
        super().__init__()

    def createGeometry(self):
        verts, norms, uvs, indices = [], [], [], []

        y_top = 0.5 * self.height
        y_bot = -0.5 * self.height

        if self.split_faces:
            # --- Sides: duplicate per quad ---
            for i in range(self.segments):
                theta1 = 2*math.pi*i/self.segments
                theta2 = 2*math.pi*(i+1)/self.segments
                x1,z1 = self.radius*math.cos(theta1), self.radius*math.sin(theta1)
                x2,z2 = self.radius*math.cos(theta2), self.radius*math.sin(theta2)
                n1 = glm.vec3(math.cos(theta1),0,math.sin(theta1))
                n2 = glm.vec3(math.cos(theta2),0,math.sin(theta2))

                base = len(verts)

                # top1
                verts.append(glm.vec4(x1,y_top,z1,1.0)); norms.append(n1); uvs.append(glm.vec2(i/self.segments,1.0))
                # bot1
                verts.append(glm.vec4(x1,y_bot,z1,1.0)); norms.append(n1); uvs.append(glm.vec2(i/self.segments,0.0))
                # top2
                verts.append(glm.vec4(x2,y_top,z2,1.0)); norms.append(n2); uvs.append(glm.vec2((i+1)/self.segments,1.0))
                # bot2
                verts.append(glm.vec4(x2,y_bot,z2,1.0)); norms.append(n2); uvs.append(glm.vec2((i+1)/self.segments,0.0))

                indices += [base, base+2, base+1, base+1, base+2, base+3]

        else:
            # --- Sides: shared ring vertices ---
            for i in range(self.segments+1):  # duplicate last for wrap
                theta = 2*math.pi*i/self.segments
                x,z = self.radius*math.cos(theta), self.radius*math.sin(theta)
                n = glm.vec3(math.cos(theta),0,math.sin(theta))
                u = i/self.segments
                verts.append(glm.vec4(x,y_top,z,1.0)); norms.append(n); uvs.append(glm.vec2(u,1.0))
                verts.append(glm.vec4(x,y_bot,z,1.0)); norms.append(n); uvs.append(glm.vec2(u,0.0))

            for i in range(self.segments):
                i0 = 2*i
                i1 = 2*i+1
                i2 = 2*(i+1)
                i3 = 2*(i+1)+1
                indices += [i0,i2,i1, i1,i2,i3]

        # --- Top cap ---
        center_top = len(verts)
        verts.append(glm.vec4(0,y_top,0,1.0)); norms.append(glm.vec3(0,1,0)); uvs.append(glm.vec2(0.5,0.5))
        for i in range(self.segments):
            theta = 2*math.pi*i/self.segments
            x,z = self.radius*math.cos(theta), self.radius*math.sin(theta)
            verts.append(glm.vec4(x,y_top,z,1.0))
            norms.append(glm.vec3(0,1,0))
            uvs.append(glm.vec2(0.5+0.5*math.cos(theta), 0.5+0.5*math.sin(theta)))
        for i in range(self.segments):
            i1 = center_top+1+i
            i2 = center_top+1+((i+1)%self.segments)
            indices += [center_top,i1,i2]

        # --- Bottom cap ---
        center_bot = len(verts)
        verts.append(glm.vec4(0,y_bot,0,1.0)); norms.append(glm.vec3(0,-1,0)); uvs.append(glm.vec2(0.5,0.5))
        for i in range(self.segments):
            theta = 2*math.pi*i/self.segments
            x,z = self.radius*math.cos(theta), self.radius*math.sin(theta)
            verts.append(glm.vec4(x,y_bot,z,1.0))
            norms.append(glm.vec3(0,-1,0))
            uvs.append(glm.vec2(0.5+0.5*math.cos(theta), 0.5-0.5*math.sin(theta))) # flip V for bottom
        for i in range(self.segments):
            i1 = center_bot+1+((i+1)%self.segments)
            i2 = center_bot+1+i
            indices += [center_bot,i1,i2]

        # Convert to numpy arrays
        self.vertices = np.array(verts,dtype=np.float32)
        self.normals  = np.array(norms,dtype=np.float32)
        self.colors   = np.full((len(verts),4), self.color, dtype=np.float32)
        self.uvs      = np.array(uvs,dtype=np.float32)
        self.indices  = np.array(indices,dtype=np.uint32)
