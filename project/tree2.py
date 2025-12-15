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
    # --- new knobs ---
    bottom_boost: float = 0.35,     # fraction of cards reserved for a dense bottom “skirt”
    bottom_band: float = 0.28,      # bottom skirt height as fraction of foliage_height
    shell_prob: float = 0.75,       # how many cards prefer the outer shell (silhouette)
):
    """
    Returns a list of glm.mat4 instance transforms for pine foliage cards.

    Key ideas:
    - Bias more cards toward the bottom (better silhouette / density).
    - Bias more cards toward the cone shell (fills outline).
    - Extra bottom “skirt” pass to guarantee density where it matters most.
    """
    T = []

    # clamp params
    bottom_boost = max(0.0, min(0.9, bottom_boost))
    bottom_band  = max(0.05, min(0.8, bottom_band))
    shell_prob   = max(0.0, min(1.0, shell_prob))

    n_main = int(count * (1.0 - bottom_boost))
    n_bottom = count - n_main

    def make_one(y: float, rr: float, r_here: float):
        ang = random.random() * 2.0 * math.pi
        x = rr * math.cos(ang)
        z = rr * math.sin(ang)

        # orientation: mostly random around Y, plus a small tilt
        yaw = random.random() * 360.0
        tiltX = (random.random() * 2.0 - 1.0) * tilt_deg
        tiltZ = (random.random() * 2.0 - 1.0) * tilt_deg

        # reduce tilt near bottom so the skirt doesn’t look “spiky”
        if foliage_height > 1e-6:
            tilt_factor = 0.30 + 0.70 * (y / foliage_height)  # 0.30 at bottom -> 1.0 at top
        else:
            tilt_factor = 1.0
        tiltX *= tilt_factor
        tiltZ *= tilt_factor

        s = min_scale + (max_scale - min_scale) * random.random()

        M = glm.mat4(1.0)
        M = glm.translate(M, glm.vec3(x, trunk_height * 0.5 + y, z))
        M = glm.rotate(M, glm.radians(yaw),   glm.vec3(0, 1, 0))
        M = glm.rotate(M, glm.radians(tiltX), glm.vec3(1, 0, 0))
        M = glm.rotate(M, glm.radians(tiltZ), glm.vec3(0, 0, 1))
        M = glm.scale(M, glm.vec3(s, s, s))
        return M

    # --- main pass: mild bottom bias + mostly shell bias ---
    for _ in range(n_main):
        t = random.random()
        y = (t ** 0.45) * foliage_height  # stronger bottom bias than your old 0.65

        # cone radius shrinks with height
        r_here = base_radius * (1.0 - (y / max(1e-6, foliage_height)))
        r_here = max(0.0, r_here)

        u = random.random()
        if random.random() < shell_prob:
            rr = (u ** 0.25) * r_here      # push outward (silhouette)
        else:
            rr = math.sqrt(u) * r_here     # some interior fill

        T.append(make_one(y, rr, r_here))

    # --- bottom skirt pass: very low + very outer ---
    for _ in range(n_bottom):
        t = random.random()
        y = (t ** 0.9) * (foliage_height * bottom_band)  # concentrate near bottom band

        r_here = base_radius * (1.0 - (y / max(1e-6, foliage_height)))
        r_here = max(0.0, r_here)

        u = random.random()
        rr = (u ** 0.12) * r_here         # very outer-heavy

        T.append(make_one(y, rr, r_here))

    return T


from framework.shapes import Cylinder
from framework.objects import MeshObject
from framework.materials import Material, Texture
# from framework.texture import Texture  # assuming you have this like grass
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEXTURE_DIR = os.path.join(BASE_DIR, "..", "textures")

def build_tree_instanced(height=6.0, width=2.0, foliage_cards=250):
    objs = []

    trunk_height   = height*0.5
    foliage_height = height*0.75

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

    leaf_texture = Texture(
        file_path=os.path.join(TEXTURE_DIR, "leaf2.png"),
        use_mipmaps=True,
        clamp_to_edge=True
    )

    foliage_mat = Material(color_texture=leaf_texture, fragment_shader="leafShader.frag", vertex_shader= "leafShader.vert")  # placeholder if you haven't wired texture/shaders yet

    foliage_mesh = FoliageCard(
        color=glm.vec4(1,1,1,1),
        width=0.9,
        height=1.2
    )

    transforms = foliage_transforms_pine(
        trunk_height=trunk_height,
        foliage_height=foliage_height,
        base_radius=width * 1.5,
        count=foliage_cards,
        tilt_deg=20.0
    )

    # IMPORTANT: use your instancing path
    # If MeshObject supports instancing via `transforms=...` (like your other code):
    foliage_obj = InstancedMeshObject(foliage_mesh, foliage_mat, transforms=transforms)
    objs.append(foliage_obj)

    return objs
