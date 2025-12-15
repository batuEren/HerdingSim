import math
import random

from framework.renderer import *
from framework.shapes import Cylinder, Cone
from framework.objects import InstancedMeshObject
from framework.materials import Material
from pyglm import glm
from foliage import *

import random
import math
from pyglm import glm

def foliage_transforms_pine(
    trunk_height: float,
    foliage_height: float,
    base_radius: float,
    count: int = 120,
    tilt_deg: float = 25.0,
    min_scale: float = 0.7,
    max_scale: float = 1.25,
):
    T = []
    for _ in range(count):
        # y in [0..foliage_height], biased a bit toward the outside/bottom looks fuller
        t = random.random()
        y = (t**0.65) * foliage_height

        # cone radius shrinks with height
        r_here = base_radius * (1.0 - (y / max(1e-6, foliage_height)))
        # sample radius in disk (sqrt for uniform area)
        rr = math.sqrt(random.random()) * r_here
        ang = random.random() * 2.0 * math.pi
        x = rr * math.cos(ang)
        z = rr * math.sin(ang)

        # orientation: mostly random around Y, plus a small tilt
        yaw   = random.random() * 360.0
        tiltX = (random.random() * 2.0 - 1.0) * tilt_deg
        tiltZ = (random.random() * 2.0 - 1.0) * tilt_deg

        s = min_scale + (max_scale - min_scale) * random.random()

        M = glm.mat4(1.0)
        M = glm.translate(M, glm.vec3(x, trunk_height*0.5 + y, z))
        M = glm.rotate(M, glm.radians(yaw),   glm.vec3(0,1,0))
        M = glm.rotate(M, glm.radians(tiltX), glm.vec3(1,0,0))
        M = glm.rotate(M, glm.radians(tiltZ), glm.vec3(0,0,1))
        M = glm.scale(M, glm.vec3(s, s, s))

        T.append(M)
    return T

from framework.shapes import Cylinder
from framework.objects import MeshObject
from framework.materials import Material
# from framework.texture import Texture  # assuming you have this like grass
# import os

def build_tree_instanced(height=6.0, width=1.0, foliage_cards=250):
    objs = []

    trunk_height   = height / 2.0
    foliage_height = height - trunk_height * 0.5

    # --- trunk ---
    log_mesh = Cylinder(
        radius=width / 4.0,
        height=trunk_height,
        color=glm.vec4(0.8, 0.5, 0.3, 1.0),
    )
    log_mat = Material()
    log_transform = glm.translate(glm.vec3(0.0, trunk_height * 0.5, 0.0))
    objs.append(MeshObject(log_mesh, log_mat, transform=log_transform))

    # --- foliage cards (instanced) ---
    # Use your foliage texture + shader that discards alpha
    # foliage_tex = Texture(file_path=os.path.join(TEXTURE_DIR, "pine_foliage.png"),
    #                      use_mipmaps=True, clamp_to_edge=True)
    # foliage_mat = Material(color_texture=foliage_tex,
    #                       vertex_shader="foliage.vert",
    #                       fragment_shader="foliage.frag")

    foliage_mat = Material()  # placeholder if you haven't wired texture/shaders yet

    foliage_mesh = FoliageCard(
        color=glm.vec4(1,1,1,1),
        width=0.9,
        height=1.2
    )

    transforms = foliage_transforms_pine(
        trunk_height=trunk_height,
        foliage_height=foliage_height,
        base_radius=width * 4.0,
        count=foliage_cards,
        tilt_deg=20.0
    )

    # IMPORTANT: use your instancing path
    # If MeshObject supports instancing via `transforms=...` (like your other code):
    foliage_obj = InstancedMeshObject(foliage_mesh, foliage_mat, transforms=transforms)
    objs.append(foliage_obj)

    return objs
