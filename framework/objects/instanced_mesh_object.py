import numpy as np
import ctypes
import OpenGL.GL as gl
from .object import *

class InstancedMeshObject(Object):
    def __init__(self, mesh, material, transforms, colors=None):
        super().__init__()
        self.mesh = mesh
        self.material = material
        self.transforms = transforms
        self.colors = colors if colors is not None else [glm.vec4(1,1,1,1)] * len(transforms)
        self.amount = len(transforms)

        self._create_instance_buffers()

    def _create_instance_buffers(self):
        # Ensure mesh VAO exists
        if getattr(self.mesh, "VAO", None) is None:
            self.mesh.createGeometry()
            self.mesh.createBuffers()

        # Flatten transforms into (amount, 16) float32
        matrices = np.array([np.array(m.to_list(), dtype=np.float32).flatten()
                             for m in self.transforms], dtype=np.float32)

        self.instanceVBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.instanceVBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, matrices.nbytes, matrices, gl.GL_STATIC_DRAW)

        gl.glBindVertexArray(self.mesh.VAO)

        # Mat4 = 4 vec4s at locations 4,5,6,7
        stride = 64  # 16 floats * 4 bytes
        for i in range(4):
            loc = 4 + i
            gl.glEnableVertexAttribArray(loc)
            gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, gl.GL_FALSE, stride, ctypes.c_void_p(i * 16))
            gl.glVertexAttribDivisor(loc, 1)

        # Optional per-instance colors at location 8
        if self.colors is not None and len(self.colors) > 0:
            loc = 8
            colors = np.array([np.array(c.to_list() if hasattr(c, "to_list") else c, dtype=np.float32)
                               for c in self.colors], dtype=np.float32)
            self.colorVBO = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.colorVBO)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, colors.nbytes, colors, gl.GL_STATIC_DRAW)

            gl.glEnableVertexAttribArray(loc)
            gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
            gl.glVertexAttribDivisor(loc, 1)

        gl.glBindVertexArray(0)

    def update_transforms(self, transforms):
        self.transforms = transforms
        matrices = np.array([np.array(m.to_list(), dtype=np.float32).flatten()
                             for m in self.transforms], dtype=np.float32)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.instanceVBO)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, matrices.nbytes, matrices)

    def update_colors(self, colors):
        self.colors = colors
        arr = np.array([np.array(c.to_list() if hasattr(c, "to_list") else c, dtype=np.float32)
                        for c in self.colors], dtype=np.float32)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.colorVBO)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, arr.nbytes, arr)

    def draw(self, camera, lights):
        self.material.set_uniforms(True, self, camera, lights)

        gl.glBindVertexArray(self.mesh.VAO)

        if self.mesh.IndexBO is not None:
            gl.glDrawElementsInstanced(gl.GL_TRIANGLES, len(self.mesh.indices), gl.GL_UNSIGNED_INT, None, self.amount)
        else:
            gl.glDrawArraysInstanced(gl.GL_TRIANGLES, 0, len(self.mesh.vertices), self.amount)

        gl.glBindVertexArray(0)
