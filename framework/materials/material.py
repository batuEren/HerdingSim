import os
import OpenGL.GL as gl
import glm
import numpy as np
from .shaders import createShader
from . import Texture

class Material:
    def __init__(self, vertex_shader="shader.vert", fragment_shader="shader.frag", color_texture=None):
        filedir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'shaders')

        defines_list = []
        self.color_texture = None
        if color_texture is not None:
            defines_list.append("USE_ALBEDO_TEXTURE")
            self.color_texture = color_texture

        self.shader_program = createShader(
            os.path.join(filedir, vertex_shader),
            os.path.join(filedir, fragment_shader),
            defines=defines_list
        )
        self.shader_program_instanced = createShader(
            os.path.join(filedir, vertex_shader),
            os.path.join(filedir, fragment_shader),
            defines=defines_list + ["INSTANCED"]
        )
        self.ambient_strength  = 0.2
        self.specular_strength = 0.5
        self.diffuse_strength = 1.0
        self.shininess         = 32.0
        self.texture_scale = glm.vec2(1.0)

    def get_shader_program(self, is_instanced):
        if is_instanced:
            return self.shader_program_instanced
        else:
            return self.shader_program

    def use(self, program):
        gl.glUseProgram(program)

    def set_uniforms(self, is_instanced, obj, camera, lights):
        program = self.get_shader_program(is_instanced)
        self.use(program)

        # Common uniforms
        loc_view = gl.glGetUniformLocation(program, "view")
        loc_projection = gl.glGetUniformLocation(program, "projection")
        gl.glUniformMatrix4fv(loc_view, 1, gl.GL_FALSE, glm.value_ptr(camera.view))
        gl.glUniformMatrix4fv(loc_projection, 1, gl.GL_FALSE, glm.value_ptr(camera.projection))

        # Only set model if non‑instanced

        loc_model = gl.glGetUniformLocation(program, "model")
        gl.glUniformMatrix4fv(loc_model, 1, gl.GL_FALSE, glm.value_ptr(obj.transform))

        # Lights
        loc_light_count = gl.glGetUniformLocation(program, "light_count")
        loc_light_pos   = gl.glGetUniformLocation(program, "light_position")
        loc_light_color = gl.glGetUniformLocation(program, "light_color")

        light_pos   = np.array([l.position for l in lights], dtype=np.float32)
        light_color = np.array([l.color for l in lights], dtype=np.float32)

        gl.glUniform1i(loc_light_count, len(lights))
        gl.glUniform4fv(loc_light_pos, len(lights), light_pos)
        gl.glUniform4fv(loc_light_color, len(lights), light_color)

        # Material Properties
        loc_ambient     = gl.glGetUniformLocation(program, "ambient_strength")
        loc_specular    = gl.glGetUniformLocation(program, "specular_strength")
        loc_diffuse     = gl.glGetUniformLocation(program, "diffuse_strength")
        loc_shiny       = gl.glGetUniformLocation(program, "shininess")

        gl.glUniform1f(loc_ambient,     self.ambient_strength)
        gl.glUniform1f(loc_specular,    self.specular_strength)
        gl.glUniform1f(loc_diffuse,     self.diffuse_strength)
        gl.glUniform1f(loc_shiny,       self.shininess)

        # Textures
        loc_scale = gl.glGetUniformLocation(program, "texture_scale")
        gl.glUniform2fv(loc_scale, 1, glm.value_ptr(self.texture_scale))

        # ALbedo texture
        if self.color_texture is not None:
            loc_sampler = gl.glGetUniformLocation(program, "albedo_texture_sampler")
            self.color_texture.bind(0)
            gl.glUniform1i(loc_sampler, 0)
