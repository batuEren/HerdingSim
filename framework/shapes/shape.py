from pyglm import glm
import numpy as np
import OpenGL.GL as gl
import ctypes

class Shape:
    def __init__(self):
        # arrays to store original vertex data
        self.vertices = np.array([], dtype=np.float32)
        self.normals  = np.array([], dtype=np.float32)
        self.colors   = np.array([], dtype=np.float32)
        self.uvs      = np.array([], dtype=np.float32)
        self.indices  = np.array([], dtype=np.uint32)

        # GL buffers
        self.VAO      = None
        self.VertexBO = None
        self.NormalBO = None
        self.ColorBO  = None
        self.UVBO     = None
        self.IndexBO  = None

    # ----------------------------
    # Buffer creation
    # ----------------------------
    def createBuffers(self):
        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        # positions
        self.VertexBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VertexBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, gl.GL_STATIC_DRAW)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # normals
        if self.normals.any():
            self.NormalBO = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.NormalBO)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, gl.GL_STATIC_DRAW)
            gl.glEnableVertexAttribArray(1)
            gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # colors
        if self.colors.any():
            self.ColorBO = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.ColorBO)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, gl.GL_STATIC_DRAW)
            gl.glEnableVertexAttribArray(2)
            gl.glVertexAttribPointer(2, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # uvs
        if self.uvs.any():
            self.UVBO = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.UVBO)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, self.uvs.nbytes, self.uvs, gl.GL_STATIC_DRAW)
            gl.glEnableVertexAttribArray(3)
            gl.glVertexAttribPointer(3, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # indices
        if self.indices.any():
            self.IndexBO = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.IndexBO)
            gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, gl.GL_STATIC_DRAW)

        gl.glBindVertexArray(0)

    # ----------------------------
    # Cleanup
    # ----------------------------
    def delete(self):
        gl.glDeleteVertexArrays(1, [self.VAO])
        gl.glDeleteBuffers(1, [self.VertexBO])
        if self.NormalBO: gl.glDeleteBuffers(1, [self.NormalBO])
        if self.ColorBO:  gl.glDeleteBuffers(1, [self.ColorBO])
        if self.UVBO:     gl.glDeleteBuffers(1, [self.UVBO])
        if self.IndexBO:  gl.glDeleteBuffers(1, [self.IndexBO])

    def update_colors(self, colors):
        self.colors = np.array(colors, dtype=np.float32)

        if self.VAO is None:
            self.createBuffers()
            return

        if self.ColorBO is None:
            gl.glBindVertexArray(self.VAO)
            self.ColorBO = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.ColorBO)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, gl.GL_STATIC_DRAW)
            gl.glEnableVertexAttribArray(2)
            gl.glVertexAttribPointer(2, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
            gl.glBindVertexArray(0)
            return

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.ColorBO)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.colors.nbytes, self.colors)
