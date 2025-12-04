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
import tree

def main():
    width, height = 600, 600
    glwindow = OpenGLWindow(width, height)

    camera = Flycamera(width, height, 70.0, 0.1, 100.0)
    camera.position += glm.vec3(0.0, 6.0, 7.0)
    camera.updateView()

    glrenderer = GLRenderer(glwindow, camera)

    glrenderer.addLight(PointLight(glm.vec4(10.0, 10.0, 10.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))

    floor_shape = Quad(width=100, height=100)
    floor_mat = Material(fragment_shader="grid.frag")
    floor_obj = MeshObject(floor_shape, floor_mat)
    floor_obj.transform = glm.rotate(glm.radians(-90), glm.vec3(1, 0, 0))
    glrenderer.addObject(floor_obj)

    cube_mesh = Cube(color=glm.vec4(0.5,0.5,1.0,1.0), side_length=1.0)
    cone_mesh = Cone(color=glm.vec4(0.5, 0.5, 1.0, 1.0), radius=1.0, height=1.0)

    cube_mat = Material()
    cube_transform = glm.translate(glm.vec3(0.0, 1.0, -2.0))
    cube_transform2 = glm.translate(glm.vec3(2.0, 1.0, -2.0))
    cone_transform = glm.translate(glm.vec3(0.0, 3.0, -2.0))

    cube_obj = MeshObject(mesh=cube_mesh, material=cube_mat, transform=cube_transform)

    cube_obj2 = MeshObject(mesh=cube_mesh, material=cube_mat, transform=cube_transform2)

    cone_obj = MeshObject(mesh=cone_mesh, material=cube_mat, transform=cone_transform)

    objs = tree.build_tree(glm.vec3(0.0, 0.0, 0.0),10.0, 2.0, 6)
    for o in objs:
        glrenderer.addObject(o)

    objs = tree.build_tree(glm.vec3(0.0, 0.0, 5.0),15.0, 3.0, 7)
    for o in objs:
        glrenderer.addObject(o)

    objs = tree.build_tree(glm.vec3(0.0, 0.0, 10.0),7.0, 1.6, 4)
    for o in objs:
        glrenderer.addObject(o)

    glrenderer.addObject(cube_obj)
    glrenderer.addObject(cone_obj)
    glrenderer.addObject(cube_obj2)

    while not glfw.window_should_close(glwindow.window):
        glrenderer.render()

    glrenderer.delete()
    glwindow.delete()
    return 0


if __name__ == "__main__":
    main()
