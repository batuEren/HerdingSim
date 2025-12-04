import OpenGL.GL as gl
import numpy as np
from pyglm import glm
from PIL import Image

class Texture:
    def __init__(self, resolution=None, data=None, file_path=None):
        """
        Create a texture either manually (width, height, optional data)
        or by loading from a file.
        """
        self.resolution = resolution
        self.data = None
        self.texture_id = None
        self.dirty = True   # needs upload

        if file_path is not None:
            self.load_from_file(file_path)
        elif self.resolution is not None:
            if data is None:
                # default: transparent black
                self.data = np.zeros((resolution.x, resolution.y, 4), dtype=np.uint8)
            else:
                self.data = np.array(data, dtype=np.uint8).reshape((resolution.y, resolution.x, 4))

    # ----------------------------
    # Loading / Saving
    # ----------------------------
    def load_from_file(self, path):
        img = Image.open(path).convert("RGBA")
        width, height = img.size
        self.resolution = glm.ivec2(width, height)
        self.data = np.array(img, dtype=np.uint8)
        self.dirty = True

    def save_to_file(self, path):
        if self.data is not None:
            img = Image.fromarray(self.data, "RGBA")
            img.save(path)

    # ----------------------------
    # Pixel Access
    # ----------------------------
    def get_pixel(self, x, y):
        return tuple(self.data[y, x])  # (R,G,B,A)

    def set_pixel(self, x, y, color: glm.vec4):
        color = glm.clamp(color, 0.0, 1.0)
        self.data[y, x] = [
            int(color.r * 255),
            int(color.g * 255),
            int(color.b * 255),
            int(color.a * 255)
        ]
        self.dirty = True

    # ----------------------------
    # GPU Upload / Binding
    # ----------------------------
    def upload(self):
        """Upload to GPU if dirty, or re-upload after edits."""
        if self.data is None:
            raise ValueError("No texture data to upload")

        if self.texture_id is None:
            self.texture_id = gl.glGenTextures(1)

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
            self.resolution.x, self.resolution.y, 0,
            gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, self.data
        )
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

        # Default parameters
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        self.dirty = False

    def bind(self, unit=0):
        """Bind texture to a texture unit, uploading if dirty."""
        if self.dirty:
            self.upload()
        gl.glActiveTexture(gl.GL_TEXTURE0 + unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)

    def release(self):
        """Free GPU resources."""
        if self.texture_id is not None:
            gl.glDeleteTextures([self.texture_id])
            self.texture_id = None
