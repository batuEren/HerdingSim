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

class ProceduralWolf:
    def __init__(self, renderer, position=glm.vec3(0,0,0), scale=1.0):
        self.renderer = renderer
        self.root = glm.translate(position) * glm.scale(glm.vec3(scale))

        # Materials (dark wolf colors)
        self.fur_mat   = Material()
        self.eye_white = Material()
        self.eye_black = Material()

        self.build_body()
        self.build_head()
        self.build_legs()
        self.build_tail()
        self.build_eyes()
        self.build_ears()
        self.build_snout()
#-----------------------------------
    def build_body(self):
        body_shape = UVSphere(1.0, color=glm.vec4(0.3,0.3,0.3,1.0))
        self.body_transform = (self.root * glm.scale(glm.vec3(1.6, 0.7, 0.7)))  # elongated wolf torso
        body = MeshObject(body_shape, self.fur_mat)
        body.transform = self.body_transform
        self.renderer.addObject(body)
#------------------------------------
    def build_head(self):
        head_shape = UVSphere(0.6, color=glm.vec4(0.35,0.35,0.35,1.0))
        self.head_transform = (self.body_transform * glm.translate(glm.vec3(1.3, 0.17, 0.0)))
        head = MeshObject(head_shape, self.fur_mat)
        head.transform = self.head_transform
        self.renderer.addObject(head)
#----------------------------------
    def build_legs(self):
        leg_shape = Cylinder(radius=0.1, height=1.25, color=glm.vec4(0.25,0.25,0.25,1.0))
        leg_offsets = [
            glm.vec3(0.6, -1.0, 0.35),
            glm.vec3(-0.6, -1.0, 0.35),
            glm.vec3(0.6, -1.0, -0.35),
            glm.vec3(-0.6, -1.0, -0.35)
        ]

        for offset in leg_offsets:
            leg = MeshObject(leg_shape, self.fur_mat)
            leg.transform = self.body_transform * glm.translate(offset)
            self.renderer.addObject(leg)
#-------------------------------------
    def build_tail(self):
        tail_color = glm.vec4(0.45, 0.45, 0.45, 1.0)

    # -------- Cone (tail base, attached to body) --------
        tail_cone_shape = Cone(
            radius=0.4,
            height=0.25,
            segments=8,
            color=tail_color
        )

        tail_cone_transform = (
            self.body_transform
            * glm.translate(glm.vec3(-1.0, 0.1, 0.0))     # back of body
            * glm.rotate(glm.radians(90), glm.vec3(0, 0, 1))  # align along -X
            * glm.rotate(glm.radians(-20), glm.vec3(0, 0, 1)) # spread out
        )
        tail_cone = MeshObject(tail_cone_shape, self.fur_mat)
        tail_cone.transform = tail_cone_transform
        self.renderer.addObject(tail_cone)

        tail_cyl = Cylinder(
            radius=0.2,
            height=0.8,
            color=tail_color
        )
        tail_cyl_transform = (tail_cone_transform * glm.translate(glm.vec3(-0.3, 0.1, 0.0))* glm.rotate(glm.radians(-90), glm.vec3(0, 0, 1))* glm.rotate(glm.radians(-15), glm.vec3(0, 0, 1)))
        cyl_obj = MeshObject(tail_cyl, self.fur_mat)
        cyl_obj.transform = tail_cyl_transform
        self.renderer.addObject(cyl_obj)
#---------------------------------------
    def build_eyes(self):
        eyeball = UVSphere(0.12, color=glm.vec4(1.0,1.0,1.0,1.0))
        pupil   = UVSphere(0.1, color=glm.vec4(0.0,0.0,0.0,1.0))

        for side in [-1, 1]:
            eye_base = (self.head_transform * glm.translate(glm.vec3(0.45, 0.15, 0.2 * side)))

            white_eye = MeshObject(eyeball, self.eye_white)
            black_eye = MeshObject(pupil, self.eye_black)

            white_eye.transform = eye_base
            black_eye.transform = eye_base * glm.translate(glm.vec3(0.05,0.0,0.0))
            self.renderer.addObject(white_eye)
            self.renderer.addObject(black_eye)
#----------------------------------------------
    def build_ears(self):
        ear_shape = Cone(radius=0.35, height=0.5, segments=4, color=glm.vec4(0.3,0.3,0.3,1.0))

        for side in [-1, 1]:
            ear_transform = (self.head_transform * glm.translate(glm.vec3(0.0, 0.45, 0.25 * side)) * glm.rotate(glm.radians(90), glm.vec3(0,0,1)))
            ear = MeshObject(ear_shape, self.fur_mat)
            ear.transform = ear_transform
            self.renderer.addObject(ear)
    #-----------------------------------
    def build_snout(self):
    # Main snout cone
        snout_cone = Cone(radius=0.18,height=0.45,segments=8,color=glm.vec4(0.4, 0.4, 0.4, 1.0))  # dark grey)

    # Nose (tip of snout)
        nose_sphere = UVSphere(0.08, color=glm.vec4(0.1, 0.1, 0.1, 1.0))  # almost black

    # ---- Cone transform ----
        snout_transform = (self.head_transform * glm.translate(glm.vec3(0.6, -0.05, 0.0)) * glm.rotate(glm.radians(-90), glm.vec3(0, 0, 1)) * glm.scale(glm.vec3(1.0, 1.2, 1.0)))  # slightly longer
        snout = MeshObject(snout_cone, self.fur_mat)
        snout.transform = snout_transform
        self.renderer.addObject(snout)

    # ---- Nose transform ----
        nose_transform = (self.head_transform * glm.translate(glm.vec3(0.6 + 0.225 - 0.04, -0.05, 0.0)))  # at tip of cone
        nose = MeshObject(nose_sphere, self.fur_mat)
        nose.transform = nose_transform
        self.renderer.addObject(nose)

def main():
    width, height = 600, 600

    # always create the window first because it initializes OpenGL
    # otherwise you might get some buffer errors
    glwindow = OpenGLWindow(width, height)

    # creates a camera that will be operated via mouse/keyboard (depending on the camera type)
    camera = Flycamera(width, height, 70.0, 0.1, 100.0)
    camera.draw_camera = False
    # raise the camera to be over the floor
    camera.position += glm.vec3(0.0, 6.0, 7.0)
    camera.updateView()

    # the renderer takes care of rendering the meshes everyframe
    # it calls internally the draw() method for every appended shape
    glrenderer = GLRenderer(glwindow, camera)

    # add light sources to the scene for shading purposes
    glrenderer.addLight(PointLight(glm.vec4(10.0, 10.0, 0.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))
    glrenderer.addLight(PointLight(glm.vec4(0.0, 10.0, 10.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))

    wolf = ProceduralWolf(glrenderer, position=glm.vec3(0, 0, 0),scale = 1.0)
    glrenderer.addObject(wolf)

    # RENDER LOOP: called every frame, here you can animate your objects
    while not glfw.window_should_close(glwindow.window):
        glrenderer.render()

    # end of render loop, deletes all necessary instances and finishes
    glrenderer.delete()
    glwindow.delete()

    return 0


if __name__ == "__main__":
    main()