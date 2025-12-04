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

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import *
from framework.renderer import *
from framework.light import *
from framework.shapes import Cube, Triangle, Quad
from framework.objects import MeshObject
from framework.materials import Material
from pyglm import glm

def main():
    width, height = 600, 600
    glwindow = OpenGLWindow(width, height)

    camera = Flycamera(width, height, 70.0, 0.1, 100.0)

    glrenderer = GLRenderer(glwindow, camera)

    glrenderer.addLight(PointLight(glm.vec4(10.0, 10.0, 10.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))

    cube_mesh = Cube(color=glm.vec4(1.0,0.0,1.0,1.0), side_length=2.0)
    cube_mat = Material()
    cube_transform = glm.translate(glm.vec3(0.0, 1.0, -2.0))
    cube_obj = MeshObject(mesh=cube_mesh, material=cube_mat, transform=cube_transform)
    glrenderer.addObject(cube_obj)

    while not glfw.window_should_close(glwindow.window):
        glrenderer.render()

    glrenderer.delete()
    glwindow.delete()
    return 0


if __name__ == "__main__":
    main()
