import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import Flycamera
from framework.window import *
from framework.renderer import *
from framework.light import *
from framework.shapes import Cube, UVSphere, Quad, Cylinder
from framework.objects import MeshObject, InstancedMeshObject
from framework.materials import Material

from pyglm import glm
import numpy as np
import random

import numpy as np
from OpenGL.GL import *

class ProceduralSheep:
    def __init__(self, renderer, position=glm.vec3(0, 0, 0), scale=1.0):
        self.renderer = renderer
        self.position = position
        self.scale = scale

        # --- Materials ---
        self.wool_mat = Material()
        self.black_mat = Material()
        self.skin_mat = Material()
        self.eye_white_mat = Material()
        self.eye_black_mat = Material()

         # Set material colors
        self.wool_mat.color = glm.vec4(1.0, 1.0, 1.0, 1.0)  # White wool
        self.black_mat.color = glm.vec4(0.1, 0.1, 0.1, 1.0)  # Black for legs
        self.skin_mat.color = glm.vec4(0.8, 0.6, 0.4, 1.0)  # Skin color
        self.eye_white_mat.color = glm.vec4(1.0, 1.0, 1.0, 1.0)  # Eye white
        self.eye_black_mat.color = glm.vec4(0.0, 0.0, 0.0, 1.0)  # Eye black

        self.build_body()
        self.build_head()
        self.build_legs()
        self.build_eyes()

    # -------------------------------------------------

    def build_body(self):
        self.body_transforms = []
        self.body_colors = []
        base_sphere = UVSphere(radius= 0.4,stacks = 6.0, split_faces = 6.0)
        self.wool_mat = Material()
        self.instance_body = InstancedMeshObject(base_sphere,self.wool_mat,
                                             transforms=self.body_transforms,
                                             colors=self.body_colors)
        self.renderer.addObject(self.instance_body)
    # -------------------------------------------------

    def build_head(self):
        self.head_transforms = []
        self.head_colors = []
        base_sphere = UVSphere(radius= 0.25,stacks = 6.0, split_faces = 6.0)
        self.wool_mat = Material()
        self.instance_body = InstancedMeshObject(base_sphere, self.head_mat,
                                                 transforms=self.head.transform,
                                                 colors=self.head_colors)
        self.renderer.addObject(self.instance_body)

    # -------------------------------------------------

    def build_legs(self):
        leg_shape = Cylinder(radius=0.07, height=0.5, stacks=6)

        leg_offsets = [
            glm.vec3( 0.25, -0.5,  0.25),
            glm.vec3( 0.25, -0.5, -0.25),
            glm.vec3(-0.25, -0.5,  0.25),
            glm.vec3(-0.25, -0.5, -0.25),
        ]

        for offset in leg_offsets:
            leg = MeshObject(leg_shape, self.skin_mat)
            transform = (
                glm.translate(self.position + offset * self.scale) *
                glm.scale(glm.vec3(1.0, 1.0, 1.0) * self.scale)
            )
            leg.transform = transform
            self.renderer.addObject(leg)

    # -------------------------------------------------

    def build_eyes(self):
        eye_shape = UVSphere(radius=0.05, stacks=6, split_faces=6, color=glm.vec4(1.0))

        pupil_shape = UVSphere(
            radius=0.02,
            stacks=6,
            split_faces=6,
            color=glm.vec4(0.0, 0.0, 0.0, 1.0)
        )

        for side in [-1, 1]:
            eye_pos = self.position + glm.vec3(0.82, 0.1, 0.08 * side)
            eye = MeshObject(eye_shape, self.eye_white_mat)
            eye.transform = glm.translate(eye_pos)
            self.renderer.addObject(eye)
            pupil = MeshObject(pupil_shape, self.eye_black_mat)
            pupil.transform = glm.translate(eye_pos + glm.vec3(0.03, 0.0, 0.0))
            self.renderer.addObject(pupil)

def main():
    width, height = 600, 600
    glwindow = OpenGLWindow(width, height)
    camera = Flycamera(width, height, 70.0, 0.1, 100.0)
    camera.draw_camera = False
    camera.position = glm.vec3(0.0, 6.0, 7.0)
    camera.updateView()
    glrenderer = GLRenderer(glwindow, camera)
    glrenderer.addLight(PointLight(glm.vec4(10.0, 10.0, 0.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))
    glrenderer.addLight(PointLight(glm.vec4(0.0, 10.0, 10.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))
    sheep = ProceduralSheep(glrenderer, position=glm.vec3(0, 0, 0), scale=1.0)
    while not glfw.window_should_close(glwindow.window):
        glrenderer.render()
        glwindow.delete()
    return 0
if __name__ == "__main__":
     main()