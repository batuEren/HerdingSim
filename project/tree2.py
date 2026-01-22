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
    upward_tilt_deg: float = 6.0,   # subtle upward bias
    min_scale: float = 0.7,
    max_scale: float = 1.25,
    bottom_boost: float = 0.35,
    bottom_band: float = 0.28,
    shell_prob: float = 0.75,
):
    """
    Returns a list of glm.mat4 instance transforms for pine foliage cards.
    Cards mostly face outward, tilt slightly upward, and vary organically.
    """
    import math, random
    import glm

    T = []

    # clamp params
    bottom_boost = max(0.0, min(0.9, bottom_boost))
    bottom_band  = max(0.05, min(0.8, bottom_band))
    shell_prob   = max(0.0, min(1.0, shell_prob))

    n_main   = int(count * (1.0 - bottom_boost))
    n_bottom = count - n_main

    def make_one(y: float, rr: float):
        ang = random.random() * 2.0 * math.pi
        x = rr * math.cos(ang)
        z = rr * math.sin(ang)

        # --- yaw: face outward radially ---
        if rr > 1e-6:
            yaw = math.degrees(math.atan2(x, z))
            yaw += random.uniform(-9.0, 9.0)  # small jitter
        else:
            yaw = random.random() * 360.0

        # --- tilt ---
        height_factor = y / max(1e-6, foliage_height)

        # base upward pitch (negative X = tilt back)
        tiltX = -upward_tilt_deg * (0.6 + 0.4 * height_factor)

        # add organic variation
        tiltX += (random.random() * 2.0 - 1.0) * tilt_deg * 0.5
        tiltZ  = (random.random() * 2.0 - 1.0) * tilt_deg * 0.5

        s = min_scale + (max_scale - min_scale) * random.random()

        M = glm.mat4(1.0)
        M = glm.translate(M, glm.vec3(x, trunk_height * 0.5 + y, z))
        M = glm.rotate(M, glm.radians(yaw),   glm.vec3(0, 1, 0))
        M = glm.rotate(M, glm.radians(tiltX), glm.vec3(1, 0, 0))
        M = glm.rotate(M, glm.radians(tiltZ), glm.vec3(0, 0, 1))
        M = glm.scale(M, glm.vec3(s, s, s))
        return M

    # --- main foliage ---
    for _ in range(n_main):
        t = random.random()
        y = (t ** 0.45) * foliage_height

        r_here = base_radius * (1.0 - y / max(1e-6, foliage_height))
        r_here = max(0.0, r_here)

        u = random.random()
        if random.random() < shell_prob:
            rr = (u ** 0.25) * r_here   # silhouette bias
        else:
            rr = math.sqrt(u) * r_here  # interior fill

        T.append(make_one(y, rr))

    # --- bottom skirt ---
    for _ in range(n_bottom):
        t = random.random()
        y = (t ** 0.9) * (foliage_height * bottom_band)

        r_here = base_radius * (1.0 - y / max(1e-6, foliage_height))
        r_here = max(0.0, r_here)

        u = random.random()
        rr = (u ** 0.12) * r_here

        T.append(make_one(y, rr))

    return T



def foliage_transforms_witness(
    trunk_height: float,
    foliage_height: float,
    base_radius: float,
    count: int = 140,

    # "Witness" feel knobs
    canopy_taper: float = 0.15,      # 0 = perfect cylinder, 0.2 = slight taper
    top_bias: float = 0.65,          # 0.5 uniform, >0.5 pushes more cards upward
    shell_prob: float = 0.85,        # prefer silhouette

    # keep cards upright
    yaw_jitter_deg: float = 25.0,    # small random yaw offset if facing-outward
    tilt_deg: float = 6.0,           # very small tilt (keeps vertical feel)

    min_scale: float = 0.85,
    max_scale: float = 1.35,

    # optional: make cards face outward from trunk (very Witness-y)
    face_outward: bool = True,

    # optional: a thin "collar" near mid/top for extra volume
    ring_boost: float = 0.25,        # fraction of cards put into a ring
    ring_center: float = 0.62,       # where ring sits (0..1 of foliage height)
    ring_width: float = 0.18,        # thickness of ring band
):
    """
    Upright / column-like foliage cards (closer to The Witness than pine cones).
    Returns list[glm.mat4].
    """
    T = []

    # clamps
    canopy_taper = max(0.0, min(0.6, canopy_taper))
    top_bias     = max(0.0, min(0.95, top_bias))
    shell_prob   = max(0.0, min(1.0, shell_prob))
    ring_boost   = max(0.0, min(0.9, ring_boost))
    ring_center  = max(0.0, min(1.0, ring_center))
    ring_width   = max(0.02, min(0.6, ring_width))

    n_ring = int(count * ring_boost)
    n_main = count - n_ring

    def radius_at(y: float) -> float:
        # mostly cylindrical canopy with gentle taper near the top
        # y in [0, foliage_height]
        if foliage_height <= 1e-6:
            return base_radius
        t = y / foliage_height
        # taper only towards the top; keeps volume vertical
        return base_radius * (1.0 - canopy_taper * (t ** 1.8))

    def sample_y_main() -> float:
        # push upward: y = 1 - (1-u)^k, k>1 => more near top
        u = random.random()
        k = 1.0 + 3.0 * top_bias
        return (1.0 - (1.0 - u) ** k) * foliage_height

    def sample_y_ring() -> float:
        # gaussian-ish around ring_center
        # simple: average a few uniforms then remap
        u = (random.random() + random.random() + random.random()) / 3.0  # ~bell
        band = ring_width * foliage_height
        y = (ring_center * foliage_height) + (u - 0.5) * band
        return max(0.0, min(foliage_height, y))

    def make_one(y: float, rr: float, ang: float):
        x = rr * math.cos(ang)
        z = rr * math.sin(ang)

        # keep cards vertical: only tiny tilt
        tiltX = (random.random() * 2.0 - 1.0) * tilt_deg
        tiltZ = (random.random() * 2.0 - 1.0) * tilt_deg

        # scale
        s = min_scale + (max_scale - min_scale) * random.random()

        # yaw: either face outward or random
        if face_outward:
            # outward-facing means yaw aligns with radial angle (billboard normal points out)
            yaw = math.degrees(ang) + 90.0  # depends on your card's forward axis
            yaw += (random.random() * 2.0 - 1.0) * yaw_jitter_deg
        else:
            yaw = random.random() * 360.0

        M = glm.mat4(1.0)
        M = glm.translate(M, glm.vec3(x, trunk_height * 0.5 + y, z))
        M = glm.rotate(M, glm.radians(yaw),   glm.vec3(0, 1, 0))
        M = glm.rotate(M, glm.radians(tiltX), glm.vec3(1, 0, 0))
        M = glm.rotate(M, glm.radians(tiltZ), glm.vec3(0, 0, 1))
        M = glm.scale(M, glm.vec3(s, s, s))
        return M

    # --- main canopy: upright column/oval, lots of mid/top volume ---
    for _ in range(n_main):
        y = sample_y_main()
        r_here = max(0.0, radius_at(y))

        u = random.random()
        if random.random() < shell_prob:
            rr = (u ** 0.22) * r_here   # outer-heavy for clean silhouette
        else:
            rr = math.sqrt(u) * r_here  # some interior fill

        ang = random.random() * 2.0 * math.pi
        T.append(make_one(y, rr, ang))

    # --- ring boost: adds that “full” witness canopy band ---
    for _ in range(n_ring):
        y = sample_y_ring()
        r_here = max(0.0, radius_at(y))

        u = random.random()
        rr = (u ** 0.16) * r_here       # very outer-heavy ring

        ang = random.random() * 2.0 * math.pi
        T.append(make_one(y, rr, ang))

    return T

from framework.shapes import Cylinder
from framework.objects import MeshObject
from framework.materials import Material, Texture
# from framework.texture import Texture  # assuming you have this like grass
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEXTURE_DIR = os.path.join(BASE_DIR, "..", "textures")

def build_tree_instanced(height=6.0, width=2.0, foliage_cards=750, leaf_color=None):
    objs = []

    trunk_height   = height*0.5
    foliage_height = height*0.75

    # --- trunk ---
    log_mesh = Cylinder(
        radius=width / 4.0,
        height=trunk_height,
        color=glm.vec4(0.8, 0.5, 0.3, 1.0),
    )

    log_texture = Texture(
        file_path=os.path.join(TEXTURE_DIR, "bark1.jpg"),
        use_mipmaps=True,
        clamp_to_edge=True
    )

    log_mat = Material(color_texture=log_texture, specular_strength=0.0)
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
        file_path=os.path.join(TEXTURE_DIR, "leaf8.png"),
        use_mipmaps=True,
        clamp_to_edge=True
    )
    if leaf_color is None:
        leaf_color = glm.vec4(0.95, 0.40, 0.02, 1.0)

    foliage_mat = Material(color_texture=leaf_texture, fragment_shader="leafShader.frag", vertex_shader= "leafShader.vert",
                           ambient_strength = 0.4, )  # placeholder if you haven't wired texture/shaders yet

    foliage_mesh = FoliageCard(
        color=leaf_color,
        width=1.8,
        height=2.0
    )

    transforms = foliage_transforms_pine(
        trunk_height=trunk_height,
        foliage_height=foliage_height,
        base_radius=width * 1.5,
        count=foliage_cards,
        tilt_deg=20.0
    )

    foliage_obj = InstancedMeshObject(foliage_mesh, foliage_mat, transforms=transforms)
    objs.append(foliage_obj)

    return objs


def build_tree_instanced2(height=6.0, width=2.0, foliage_cards=750, leaf_color=None):
    objs = []

    trunk_height   = height*0.5
    foliage_height = height*0.75

    # --- trunk ---
    log_mesh = Cylinder(
        radius=width / 4.0,
        height=trunk_height,
        color=glm.vec4(0.8, 0.5, 0.3, 1.0),
    )

    log_texture = Texture(
        file_path=os.path.join(TEXTURE_DIR, "bark1.jpg"),
        use_mipmaps=True,
        clamp_to_edge=True
    )

    log_mat = Material(color_texture=log_texture, specular_strength= 0.0, shininess=64.0)
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
        file_path=os.path.join(TEXTURE_DIR, "leaf8.png"),
        use_mipmaps=True,
        clamp_to_edge=True
    )
    if leaf_color is None:
        leaf_color = glm.vec4(0.95, 0.40, 0.02, 1.0)

    foliage_mat = Material(color_texture=leaf_texture, fragment_shader="leafShader.frag", vertex_shader= "leafShader.vert")  # placeholder if you haven't wired texture/shaders yet

    foliage_mesh = FoliageCard(
        color=leaf_color,
        width=1.0,
        height=1.0
    )

    transforms = foliage_transforms_witness(
        trunk_height=trunk_height,
        foliage_height=foliage_height,
        base_radius=width * 1.5,
        count=foliage_cards,
    )

    foliage_obj = InstancedMeshObject(foliage_mesh, foliage_mat, transforms=transforms)
    objs.append(foliage_obj)

    return objs
