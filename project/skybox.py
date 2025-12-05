import OpenGL.GL as gl
import numpy as np
from pyglm import glm
from PIL import Image

class Skybox:
    def __init__(self, faces, material):
        """
        faces  : list of 6 cube-map face paths [right, left, top, bottom, front, back]
        material : a Material instance using skybox.vert/skybox.frag
        """
        self.material = material
        self.program = material.get_shader_program(is_instanced=False)
        self.cubemap_tex = self._load_cubemap(faces)
        self.vao = self._create_cube()

    def _create_cube(self):
        vertices = np.array([
            # positions
            -1.0,  1.0, -1.0,
            -1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
             1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,

            -1.0, -1.0,  1.0,
            -1.0, -1.0, -1.0,
            -1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,
            -1.0,  1.0,  1.0,
            -1.0, -1.0,  1.0,

             1.0, -1.0, -1.0,
             1.0, -1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0, -1.0,
             1.0, -1.0, -1.0,

            -1.0, -1.0,  1.0,
            -1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0, -1.0,  1.0,
            -1.0, -1.0,  1.0,

            -1.0,  1.0, -1.0,
             1.0,  1.0, -1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
            -1.0,  1.0,  1.0,
            -1.0,  1.0, -1.0,

            -1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,
             1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,
             1.0, -1.0,  1.0
        ], dtype=np.float32)

        vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * 4, None)

        gl.glBindVertexArray(0)
        return vao

    def _load_cubemap(self, faces):
        tex_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, tex_id)

        for i, path in enumerate(faces):
            img = Image.open(path).convert("RGB")
            w, h = img.size

            # (optional) resize to square if needed
            # if w != h:
            #     size = min(w, h)
            #     img = img.resize((size, size), Image.LANCZOS)
            #     w = h = size

            data = np.array(img, dtype=np.uint8)

            gl.glTexImage2D(
                gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                0,
                gl.GL_RGB,
                w, h,
                0,
                gl.GL_RGB,
                gl.GL_UNSIGNED_BYTE,
                data
            )

        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, 0)
        return tex_id

    def draw(self, camera, lights):
        # Use same matrices as Material: camera.view, camera.projection
        view = camera.view
        proj = camera.projection

        # remove translation so the skybox doesn’t move
        view_no_trans = glm.mat4(glm.mat3(view))

        gl.glDepthFunc(gl.GL_LEQUAL)

        program = self.program
        self.material.use(program)

        loc_view = gl.glGetUniformLocation(program, "view")
        loc_proj = gl.glGetUniformLocation(program, "projection")
        gl.glUniformMatrix4fv(loc_view, 1, gl.GL_FALSE, glm.value_ptr(view_no_trans))
        gl.glUniformMatrix4fv(loc_proj, 1, gl.GL_FALSE, glm.value_ptr(proj))

        # samplerCube skybox
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.cubemap_tex)
        loc_skybox = gl.glGetUniformLocation(program, "skybox")
        gl.glUniform1i(loc_skybox, 0)

        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
        gl.glBindVertexArray(0)

        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, 0)
        gl.glDepthFunc(gl.GL_LESS)
