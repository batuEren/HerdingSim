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
from framework.materials import Material
from pyglm import glm
import tree
from fence import *
from terrain import *
from skybox import *
from collections import defaultdict



def main():
    width, height = 600, 600
    glwindow = OpenGLWindow(width, height)

    camera = Flycamera(width, height, 70.0, 0.1, 200.0)
    camera.position += glm.vec3(0.0, 6.0, 7.0)
    camera.updateView()

    glrenderer = GLRenderer(glwindow, camera)

    glrenderer.addLight(PointLight(glm.vec4(10.0, 10.0, 10.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))

    #floor_shape = Quad(width=100, height=100)
    #floor_mat = Material(fragment_shader="grid.frag")
    #floor_obj = MeshObject(floor_shape, floor_mat)
    #floor_obj.transform = glm.rotate(glm.radians(-90), glm.vec3(1, 0, 0))
    #glrenderer.addObject(floor_obj)

    terrain_width = 200
    terrain_depth = 200

    terrain_shape = Terrain(
        width=terrain_width,
        depth=terrain_depth,
        res_x=50,  # increase for smoother geometry
        res_z=50,
        color=glm.vec4(0.2, 0.8, 0.3, 1.0)
    )

    terrain_mat = Material(fragment_shader="shaderGrid.frag")
    terrain_obj = MeshObject(terrain_shape, terrain_mat)

    terrain_obj.transform = glm.mat4(1.0)

    glrenderer.addObject(terrain_obj)

    # -- TREE STUFF --

    def createRandomTrees(amount):
        treeTypes = []
        for i in range(0, amount):
            size = random.random()
            segments = int(3 + size * 6)
            objs = tree.build_tree(
                3 + 8.0 * size + random.random(),
                1 + 2.0 * size + 0.5 * random.random(),
                segments
            )
            treeTypes.append(objs)
        return treeTypes

    treeTypes = createRandomTrees(5)

    tree_instances = defaultdict(list)

    def putRandomTree(treeTypes, x, z):
        rand = random.randrange(len(treeTypes))
        template_objs = treeTypes[rand]

        base_y = random_height_func(x, z)
        tree_translation = glm.translate(glm.mat4(1.0), glm.vec3(x, base_y, z))

        for o in template_objs:
            M = tree_translation * o.transform
            tree_instances[(id(o.mesh), id(o.material))].append((o.mesh, o.material, M))

    for x in range(0,terrain_width, 7):
        for z in range(0, terrain_depth, 7):
            putRandomTree(treeTypes, x-(terrain_width/2)+random.randint(0, 10), z-(terrain_depth/2)+random.randint(0, 10))

    for key, items in tree_instances.items():
        mesh, mat, _ = items[0]
        matrices = [M for (_, _, M) in items]
        instanced_obj = InstancedMeshObject(mesh, mat, matrices)
        glrenderer.addObject(instanced_obj)


    # -- FENCE --
    def buildFence(fence_start = glm.vec3(-40.0, 0.0, -40.0), fence_end   = glm.vec3( 40.0, 0.0, -40.0)):
        fence_objs = build_fence(
            fence_start,
            fence_end,
            spacing=3.0,
            height_func=random_height_func
        )

        for o in fence_objs:
            glrenderer.addObject(o)

    rad = 15

    buildFence(glm.vec3(-rad, 0.0, -rad), glm.vec3(rad, 0.0, -rad))
    buildFence(glm.vec3(rad, 0.0, -rad), glm.vec3(rad, 0.0, rad))
    buildFence(glm.vec3(rad, 0.0, rad), glm.vec3(-rad, 0.0, rad))
    buildFence(glm.vec3(-rad, 0.0, rad), glm.vec3(-rad, 0.0, -rad))

    # -- SKYBOX --

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

    while not glfw.window_should_close(glwindow.window):
        glrenderer.render()

    glrenderer.delete()
    glwindow.delete()
    return 0


if __name__ == "__main__":
    main()
