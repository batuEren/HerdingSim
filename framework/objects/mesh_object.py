from pyglm import glm
from .object import *
import OpenGL.GL as gl

class MeshObject(Object):
    def __init__(self, mesh, material, transform=glm.mat4(1.0)):
        super().__init__(transform)
        self.mesh = mesh
        self.material = material
        self.visible = True

    def draw(self, camera, lights):
        if self.visible == False:
            return
        prev_blend = gl.glIsEnabled(gl.GL_BLEND)
        if getattr(self.material, "blend", False):
            gl.glEnable(gl.GL_BLEND)
        else:
            gl.glDisable(gl.GL_BLEND)

        self.material.set_uniforms(False, self, camera, lights)

        if self.mesh.VAO is None:
            self.mesh.createGeometry()
            self.mesh.createBuffers()

        gl.glBindVertexArray(self.mesh.VAO)

        if self.mesh.IndexBO is not None:
            gl.glDrawElements(gl.GL_TRIANGLES, len(self.mesh.indices), gl.GL_UNSIGNED_INT, None)
        else:
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.mesh.vertices))

        gl.glBindVertexArray(0)
        if prev_blend:
            gl.glEnable(gl.GL_BLEND)
        else:
            gl.glDisable(gl.GL_BLEND)
