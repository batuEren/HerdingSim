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
    def __init__(self, renderer, position=glm.vec3(0,0,0), scale = 1.0):
        self.renderer = renderer
        self.root = (glm.translate(position)   * glm.scale(glm.vec3(scale))
        )

        # Materials
        self.wool_mat = Material()
        self.head_mat = Material()
        self.skin_mat = Material()
        self.eye_white = Material()
        self.eye_black = Material()

        self.build_body()
        self.build_head()
        self.build_legs()
        self.build_eyes()
        self.build_ears()
        # ------------------ BODY ------------------
    def build_body(self):
        body_shape = UVSphere(1.0, color=glm.vec4(1.0))
        self.body_transform = self.root * glm.scale(glm.vec3(1.0, 0.9, 0.9))
        body = MeshObject(body_shape, self.wool_mat)
        body.transform = self.body_transform
        self.renderer.addObject(body)

    # ------------------ HEAD ------------------
    def build_head(self):
        head_shape = UVSphere(0.6, color=glm.vec4(0.5, 0.5, 0.5, 1.0))
        self.head_transform = self.body_transform * glm.translate(glm.vec3(1.2,0.2,0.0))
        head = MeshObject(head_shape, self.head_mat)
        head.transform = self.head_transform
        self.renderer.addObject(head)

    # ------------------ LEGS ------------------
    def build_legs(self):
        leg_shape = Cylinder(radius=0.1, height=0.6, color=glm.vec4(0.3, 0.3, 0.3, 1.0))
        leg_offsets = [
            glm.vec3(0.5, -0.55, 0.4),   # front-right
            glm.vec3(-0.5, -0.55, 0.4),  # front-left
            glm.vec3(0.5, -0.55, -0.4),  # back-right
            glm.vec3(-0.5, -0.55, -0.5)  # back-left
            ]
        for offset in leg_offsets:
            leg = MeshObject(leg_shape, self.skin_mat)
            leg.transform = self.body_transform * glm.translate(offset)
            self.renderer.addObject(leg)

# ------------------ EYES ------------------
    def build_eyes(self):
        eyeball = UVSphere(0.12, color=glm.vec4(1.0, 1.0, 1.0, 1.0))
        pupil = UVSphere(0.06, color=glm.vec4(0.0, 0.0, 0.0, 1.0))
        for side in [-1, 1]:
            eye_base = self.head_transform * glm.translate(glm.vec3(0.45, 0.15, 0.2*side))  # move forward and up
            white_eye = MeshObject(eyeball, self.eye_white)
            white_eye.transform = eye_base
            black_pupil = MeshObject(pupil, self.eye_black)
            black_pupil.transform = eye_base * glm.translate(glm.vec3(0.06, 0.0, 0.0))
            self.renderer.addObject(white_eye)
            self.renderer.addObject(black_pupil)

    # ------------------ EARS ------------------
    def build_ears(self):
        ear_shape = Cone(radius=0.15, height=0.25, segments=4, color=glm.vec4(0.5, 0.5, 0.5, 1.0))
        for side in [-1,1]:
            ear_transform = (
                self.head_transform
                * glm.translate(glm.vec3(0.0,0.35,0.35*side))
                * glm.rotate(glm.radians(90), glm.vec3(0,0,1))
                * glm.scale(glm.vec3(1.0,0.5,1.0))
            )
            ear = MeshObject(ear_shape, self.head_mat)
            ear.transform = ear_transform
            self.renderer.addObject(ear)

    #-------------------------------------------------
def main():
    width, height = 600, 600
    glwindow = OpenGLWindow(width, height)
    glwindow = OpenGLWindow(width, height)
    glfw.make_context_current(glwindow.window)  # sometimes required depending on framework
    camera = Flycamera(width, height, 700.0, 0.1, 100.0)
    camera.draw_camera = False
    camera.position = glm.vec3(0.0, 6.0, 7.0)
    camera.updateView()
    glrenderer = GLRenderer(glwindow, camera)
    glrenderer.addLight(PointLight(glm.vec4(10.0, 10.0, 0.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))
    glrenderer.addLight(PointLight(glm.vec4(0.0, 10.0, 10.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))
    sheep = ProceduralSheep(glrenderer, position=glm.vec3(0, 0, 0),scale = 1.0)
    while not glfw.window_should_close(glwindow.window):
        glrenderer.render()
    glwindow.delete()
    return 
if __name__ == "__main__":
     main()
