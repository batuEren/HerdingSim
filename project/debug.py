"""

  /$$$$$$$  /$$   /$$ /$$$$$$$$ /$$$$$$   /$$$$$$  /$$   /$$
 | $$__  $$| $$  /$$/|_____ $$//$$$_  $$ /$$__  $$| $$  | $$
 | $$  \\ $$| $$ /$$/      /$$/| $$$$\\ $$| $$  \\ $$| $$  | $$
 | $$$$$$$ | $$$$$/      /$$/ | $$ $$ $$|  $$$$$$/| $$$$$$$$
 | $$__  $$| $$  $$     /$$/  | $$\\ $$$$ >$$__  $$|_____  $$
 | $$  \\ $$| $$\\  $$   /$$/   | $$ \\ $$$| $$  \\ $$      | $$
 | $$$$$$$/| $$ \\  $$ /$$/    |  $$$$$$/|  $$$$$$/      | $$
 |_______/ |__/  \\__/|__/      \\______/  \\______/       |__/

"""
import random
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import *
from framework.renderer import *
from framework.light import *
from framework.shapes import Cube, Triangle, Quad
from framework.objects import MeshObject, InstancedMeshObject
from framework.materials import Material, Texture
from pyglm import glm
import tree
import tree2
from fence import *
from grass import *
from terrain import *
from skybox import *
from collections import defaultdict
from OpenGL.GL import *




def main():
    width, height = 600, 600
    glwindow = OpenGLWindow(width, height)

    camera = Flycamera(width, height, 70.0, 0.1, 300.0)
    camera.position += glm.vec3(0.0, 6.0, 7.0)
    camera.updateView()

    glrenderer = GLRenderer(glwindow, camera)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glrenderer.addLight(PointLight(glm.vec4(000.0, 5000.0, 3000.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEXTURE_DIR = os.path.join(BASE_DIR, "..", "textures")

    # -- TREE STUFF --

    objs = tree2.build_tree_instanced2(height = 12.0, width=3.0, foliage_cards=850)
    for o in objs:
        glrenderer.addObject(o)



    # -- SKYBOX --
    faces = [
        os.path.join(TEXTURE_DIR, "right.png"),
        os.path.join(TEXTURE_DIR, "left.png"),
        os.path.join(TEXTURE_DIR, "top.png"),
        os.path.join(TEXTURE_DIR, "bottom.png"),
        os.path.join(TEXTURE_DIR, "front.png"),
        os.path.join(TEXTURE_DIR, "back.png"),
    ]

    skybox_mat = Material(fragment_shader="skybox.frag", vertex_shader="skybox.vert")
    skybox = Skybox(faces, skybox_mat)

    glrenderer.setSkybox(skybox)

    while not glfw.window_should_close(glwindow.window):
        glrenderer.render()

    glrenderer.delete()
    glwindow.delete()
    return 0


if __name__ == "__main__":
    main()
