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
from framework.objects import MeshObject
from framework.materials import Material
from pyglm import glm
import tree
from terrain import *
from skybox import *



def main():
    width, height = 600, 600
    glwindow = OpenGLWindow(width, height)

    camera = Flycamera(width, height, 70.0, 0.1, 100.0)
    camera.position += glm.vec3(0.0, 6.0, 7.0)
    camera.updateView()

    glrenderer = GLRenderer(glwindow, camera)

    glrenderer.addLight(PointLight(glm.vec4(10.0, 10.0, 10.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))

    #floor_shape = Quad(width=100, height=100)
    #floor_mat = Material(fragment_shader="grid.frag")
    #floor_obj = MeshObject(floor_shape, floor_mat)
    #floor_obj.transform = glm.rotate(glm.radians(-90), glm.vec3(1, 0, 0))
    #glrenderer.addObject(floor_obj)

    terrain_width = 100
    terrain_depth = 100

    terrain_shape = Terrain(
        width=terrain_width,
        depth=terrain_depth,
        res_x=200,  # increase for smoother geometry
        res_z=200,
        color=glm.vec4(0.2, 0.8, 0.3, 1.0)
    )

    terrain_mat = Material(fragment_shader="shaderGrid.frag")
    terrain_obj = MeshObject(terrain_shape, terrain_mat)

    terrain_obj.transform = glm.mat4(1.0)

    glrenderer.addObject(terrain_obj)

    cube_mesh = Cube(color=glm.vec4(0.5,0.5,1.0,1.0), side_length=1.0)
    cone_mesh = Cone(color=glm.vec4(0.5, 0.5, 1.0, 1.0), radius=1.0, height=1.0)

    cube_mat = Material()
    cube_transform = glm.translate(glm.vec3(0.0, 1.0, -2.0))
    cube_transform2 = glm.translate(glm.vec3(2.0, 1.0, -2.0))
    cone_transform = glm.translate(glm.vec3(0.0, 3.0, -2.0))

    cube_obj = MeshObject(mesh=cube_mesh, material=cube_mat, transform=cube_transform)

    cube_obj2 = MeshObject(mesh=cube_mesh, material=cube_mat, transform=cube_transform2)

    cone_obj = MeshObject(mesh=cone_mesh, material=cube_mat, transform=cone_transform)

    def createRandomTree(x, z):
        size = random.random()
        segments = (int)(3+size*6)
        objs = tree.build_tree(glm.vec3(x, random_height_func(x,z), z), 3+8.0*size+random.random(), 1+2.0*size+0.5*random.random(), segments)
        for o in objs:
            glrenderer.addObject(o)

    for x in range(0,terrain_width, 25):
        for z in range(0, terrain_depth, 25):
            createRandomTree(x-50+random.randint(0, 10), z-50+random.randint(0, 10))

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEXTURE_DIR = os.path.join(BASE_DIR, "..", "textures")

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
