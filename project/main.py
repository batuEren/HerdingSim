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
    #glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glEnable(GL_MULTISAMPLE)
    glEnable(GL_SAMPLE_ALPHA_TO_COVERAGE)
    glDisable(GL_BLEND)  # usually best with A2C for cutout foliage
    glDepthMask(GL_TRUE)  # keep writing depth so grass self-occludes nicely

    glrenderer.addLight(PointLight(glm.vec4(000.0, 5000.0, 3000.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEXTURE_DIR = os.path.join(BASE_DIR, "..", "textures")

    # -- TERRAIN --

    terrain_width = 200
    terrain_depth = 200

    colorRand = random.random()
    ground_color = glm.vec4(0.50 + 0.05 * colorRand, 0.45 + 0.05 * colorRand, 0.06 + 0.01 * colorRand, 1.0)

    terrain_shape = Terrain(
        width=terrain_width,
        depth=terrain_depth,
        res_x=50,  # increase for smoother geometry
        res_z=50,
        color=ground_color
    )

    terrain_mat = Material(fragment_shader="shader.frag")
    terrain_obj = MeshObject(terrain_shape, terrain_mat)

    terrain_obj.transform = glm.mat4(1.0)

    glrenderer.addObject(terrain_obj)

    # -- GRASS --

    grass_color = glm.vec4(0.50 + 0.05 * colorRand, 0.45 + 0.05 * colorRand, 0.06 + 0.01 * colorRand, 1.0)
    grass_mesh = Grass(radius=0.45, height=0.9, color=grass_color)
    grass_texture = Texture(
        file_path=os.path.join(TEXTURE_DIR, "grass9.png"),
        use_mipmaps=True,
        clamp_to_edge=True
    )
    grass_mat = Material(color_texture=grass_texture, fragment_shader="grassShader.frag", vertex_shader= "grassShader.vert")

    grass_obj = MeshObject(grass_mesh, grass_mat)
    grass_obj.transform = glm.translate(glm.vec3(1.0, 10, 1.0))
    glrenderer.addObject(grass_obj) #test obj

    def terrain_normal(x, z, eps=0.2):
        hL = random_height_func(x - eps, z)
        hR = random_height_func(x + eps, z)
        hD = random_height_func(x, z - eps)
        hU = random_height_func(x, z + eps)

        dhdx = (hR - hL) / (2.0 * eps)
        dhdz = (hU - hD) / (2.0 * eps)

        # normal points “up” from the slope
        n = glm.vec3(-dhdx, 1.0, -dhdz)
        return glm.normalize(n)

    def align_up_to_normal(n):
        up = glm.vec3(0, 1, 0)

        # if nearly flat, no tilt needed
        if abs(glm.dot(up, n)) > 0.9999:
            return glm.mat4(1.0)

        axis = glm.normalize(glm.cross(up, n))
        angle = glm.acos(glm.clamp(glm.dot(up, n), -1.0, 1.0))
        return glm.rotate(glm.mat4(1.0), angle, axis)

    transforms = []
    step = 0.3
    jitter = 0.5
    density = 0.95


    x = 0
    while(x < terrain_width):
        z = 0
        while(z < terrain_depth):
            if random.random() > density:
                z += step
                continue

            wx = x + (random.random() * 2.0 - 1.0) * jitter - terrain_width / 2
            wz = z + (random.random() * 2.0 - 1.0) * jitter - terrain_depth / 2
            wy = random_height_func(wx, wz)

            yaw = random.random() * 6.28318530718
            s = 0.7 + random.random() * 0.7

            n = terrain_normal(wx, wz)

            T = glm.translate(glm.vec3(wx, wy, wz))

            Rtilt = align_up_to_normal(n)
            Ryaw = glm.rotate(glm.mat4(1.0), yaw, n)  # yaw around ground normal

            S = glm.scale(glm.vec3(s, 1.0, s))

            transforms.append(T * Rtilt * Ryaw * S)

            z += step
        x += step


    grass_colors = [grass_mesh.color] * len(transforms)

    grass_inst = InstancedMeshObject(grass_mesh, grass_mat, transforms, grass_colors)
    glrenderer.addObject(grass_inst)


    # -- TREE --

    def createRandomTrees(amount):
        treeTypes = []
        for i in range(amount):
            size = random.random()

            objs = tree2.build_tree_instanced(
                8 + 16.0 * size,
                2 + 4.0 * size,
                foliage_cards=1500+(int)(size*2000)
            )
            treeTypes.append(objs)
        return treeTypes

    treeTypes = createRandomTrees(5)

    # store only matrices (and optional per-instance colors) per instancing group
    tree_instances = defaultdict(list)

    def _is_instanced_obj(o):
        # adapt if your class names differ
        return isinstance(o, InstancedMeshObject) or hasattr(o, "transforms")

    def putRandomTree(treeTypes, x, z):
        rand = random.randrange(len(treeTypes))
        template_objs = treeTypes[rand]

        base_y = random_height_func(x, z)
        tree_translation = glm.translate(glm.mat4(1.0), glm.vec3(x, base_y, z))

        for o in template_objs:
            # local transform of that object inside the tree (trunk offset, foliage offset, etc.)
            local_obj = getattr(o, "transform", glm.mat4(1.0))
            obj_world = tree_translation * local_obj

            key = (id(o.mesh), id(o.material))

            if _is_instanced_obj(o):
                # foliage: flatten (tree * obj_local) * leaf_local
                leaf_transforms = getattr(o, "transforms", None)
                if leaf_transforms is None:
                    # some implementations store matrices under a different name
                    leaf_transforms = getattr(o, "matrices", [])

                for L in leaf_transforms:
                    tree_instances[key].append(obj_world * L)
            else:
                # trunk: single matrix
                tree_instances[key].append(obj_world)

    # --- place many trees ---
    step = 20
    for x in range(0, terrain_width, step):
        for z in range(0, terrain_depth, step):
            putRandomTree(
                treeTypes,
                x - (terrain_width / 2) + random.randint(0, 10),
                z - (terrain_depth / 2) + random.randint(0, 10),
            )

    # --- build final instanced objects ---
    for key, matrices in tree_instances.items():
        mesh = None
        mat = None
        for t in treeTypes:
            for o in t:
                if (id(o.mesh), id(o.material)) == key:
                    mesh, mat = o.mesh, o.material
                    break
            if mesh is not None:
                break

        if mesh is None:
            continue

        # If your InstancedMeshObject expects colors, you can still pass them
        colors = [mesh.color] * len(matrices) if hasattr(mesh, "color") else None

        if colors is None:
            instanced_obj = InstancedMeshObject(mesh, mat, matrices)
        else:
            instanced_obj = InstancedMeshObject(mesh, mat, matrices, colors)

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
