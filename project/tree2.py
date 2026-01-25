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
    base_offset: float = 0.0,
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
        M = glm.translate(M, glm.vec3(x, trunk_height * 0.5 + base_offset + y, z))
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
    base_offset: float = 0.0,
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
        M = glm.translate(M, glm.vec3(x, trunk_height * 0.5 + base_offset + y, z))
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

_LOG_MESH = None
_LOG_MAT = None


def _get_shared_log_resources():
    global _LOG_MESH, _LOG_MAT
    if _LOG_MESH is None:
        _LOG_MESH = Cylinder(radius=1.0, height=1.0, color=glm.vec4(1.0))
    if _LOG_MAT is None:
        log_texture = Texture(
            file_path=os.path.join(TEXTURE_DIR, "bark1.jpg"),
            use_mipmaps=True,
            clamp_to_edge=True
        )
        _LOG_MAT = Material(color_texture=log_texture, specular_strength=0.0)
    return _LOG_MESH, _LOG_MAT


class LSystemLog:
    """
    Pine-ish L-system log made of instanced cylinders.
    Generates local-space transforms; caller can place the object in the world.
    """
    def __init__(
        self,
        target_height: float,
        target_radius: float,
        depth: int = 5,
        base_length: float = 1.0,
        yaw_deg: float = 25.0,
        pitch_deg: float = 25.0,
        roll_deg: float = 25.0,
        length_scale: float = 0.82,
        random_angle_jitter_deg: float = 15.0,
        random_len_jitter: float = 0.08,
        trunk_rot_jitter_deg: float = 4.0,
        branch_rot_jitter_deg: float = 15.0,
        radius_mode: str = "length_depth",
        radius_scale: float = 0.95,
        branch_radius_scale: float = 0.65,
        min_radius=None,
        branch_base_multiplier: float = 0.55,
        branch_droop_deg: float = 30.0,
        height_taper: float = 0.2,
        trunk_jitter_factor: float = 0.25,
        mesh=None,
        material=None,
    ):
        self.depth = depth
        self.base_length = float(base_length)

        self.yaw = glm.radians(yaw_deg)
        self.pitch = glm.radians(pitch_deg)
        self.roll = glm.radians(roll_deg)

        self.length_scale = length_scale
        self.ang_jitter = glm.radians(random_angle_jitter_deg)
        self.len_jitter = random_len_jitter
        self.trunk_rot_jitter = glm.radians(trunk_rot_jitter_deg)
        self.branch_rot_jitter = glm.radians(branch_rot_jitter_deg)

        self.base_radius = float(target_radius)
        self.radius_mode = radius_mode
        self.radius_scale = float(radius_scale)
        self.branch_radius_scale = float(branch_radius_scale)
        if min_radius is None:
            min_radius = max(0.02, self.base_radius * 0.08)
        self.min_radius = float(min_radius)

        self.branch_base_multiplier = float(branch_base_multiplier)
        self.branch_droop = glm.radians(branch_droop_deg)
        self.height_taper = float(height_taper)
        self.trunk_jitter_factor = float(trunk_jitter_factor)

        axiom = "A"
        rules = {
            "A": "F[+B][-B][\\B][/B][&B][^B]GGA",
            "B": "F[+F]F[-F]F[\\F]F[/F]"
        }

        s = self._expand_lsystem(axiom, rules, depth)

        transforms, colors, max_height = self._interpret(s, return_max_height=True)
        if max_height > 1e-6 and target_height > 0.0:
            height_scale = float(target_height) / max_height
            if abs(height_scale - 1.0) > 1e-6:
                self.base_length *= height_scale
                transforms, colors = self._interpret(s, return_max_height=False)

        if mesh is None or material is None:
            mesh, material = _get_shared_log_resources()

        self.mesh = mesh
        self.material = material
        self.transforms = transforms
        self.colors = colors
        self.object = InstancedMeshObject(mesh, material, transforms=transforms, colors=colors)

    def _expand_lsystem(self, axiom, rules, iters):
        s = axiom
        for _ in range(iters):
            s = "".join(rules.get(ch, ch) for ch in s)
        return s

    def _interpret(self, s, return_max_height=False):
        class State:
            def __init__(self, pos, q, length, depth, sym):
                self.pos = pos
                self.q = q
                self.length = length
                self.depth = depth
                self.sym = sym

            def clone(self):
                return State(glm.vec3(self.pos), glm.quat(self.q), self.length, self.depth, self.sym)

        def jitter_angle(base, st):
            j = self.ang_jitter * (self.trunk_jitter_factor if st.sym == "A" else 1.0)
            return base + j * (random.random() - 0.5)

        def jitter_length(L):
            return L * (1.0 + self.len_jitter * (random.random() - 0.5))

        def apply_random_rot(st: State):
            jitter = self.trunk_rot_jitter if st.sym == "A" else self.branch_rot_jitter
            if jitter <= 1e-8:
                return
            rx = jitter * (random.random() - 0.5)
            ry = jitter * (random.random() - 0.5)
            rz = jitter * (random.random() - 0.5)
            right_world = glm.mat3_cast(st.q) * glm.vec3(1, 0, 0)
            up_world = glm.mat3_cast(st.q) * glm.vec3(0, 0, 1)
            fwd_world = glm.mat3_cast(st.q) * glm.vec3(0, 1, 0)
            qx = glm.angleAxis(rx, glm.normalize(right_world))
            qy = glm.angleAxis(ry, glm.normalize(up_world))
            qz = glm.angleAxis(rz, glm.normalize(fwd_world))
            st.q = glm.normalize(qz * qy * qx * st.q)

        def compute_radius(st: State) -> float:
            r_len = (st.length / self.base_length) if self.base_length > 1e-8 else 1.0
            depth_scale = self.radius_scale if st.sym == "A" else self.branch_radius_scale
            r_depth = (depth_scale ** st.depth)

            if self.radius_mode == "length":
                r = self.base_radius * r_len
            elif self.radius_mode == "depth":
                r = self.base_radius * r_depth
            else:
                r = self.base_radius * r_len * r_depth

            return max(self.min_radius, r)

        st = State(
            pos=glm.vec3(0, 0, 0),
            q=glm.quat(),
            length=self.base_length,
            depth=0,
            sym="A"
        )
        stack = []

        transforms = []
        colors = []
        max_height = 0.0

        for ch in s:
            if ch == "F":
                R = glm.mat4_cast(st.q)

                mid_local = glm.vec3(0, st.length * 0.5, 0)
                tip_local = glm.vec3(0, st.length, 0)

                radius = compute_radius(st)

                T = (
                    glm.translate(st.pos)
                    * R
                    * glm.translate(mid_local)
                    * glm.scale(glm.vec3(radius, st.length, radius))
                )
                transforms.append(T)

                c = min(1.0, max(0.0, st.length / (self.base_length * 1.5)))
                colors.append(glm.vec4(c, c, c, 1.0))

                tip_world = st.pos + (R * glm.vec4(tip_local, 0.0)).xyz
                max_height = max(max_height, float(tip_world.y))

                st.pos = tip_world
                st.length = jitter_length(st.length * self.length_scale)
            elif ch == "G":
                R = glm.mat4_cast(st.q)
                tip_local = glm.vec3(0, st.length, 0)
                st.pos = st.pos + (R * glm.vec4(tip_local, 0.0)).xyz
                max_height = max(max_height, float(st.pos.y))
                st.length = jitter_length(st.length * self.length_scale)

            elif ch == "[":
                st.depth += 1
                stack.append(st.clone())

            elif ch == "]":
                st = stack.pop()

            elif ch == "A":
                st.sym = "A"

            elif ch == "B":
                st.sym = "B"

                height = max(0.0, float(st.pos.y))
                height_factor = 1.0 / (1.0 + self.height_taper * height)

                st.length *= (self.branch_base_multiplier * height_factor)

                right_world = glm.mat3_cast(st.q) * glm.vec3(1, 0, 0)
                st.q = glm.normalize(glm.angleAxis(self.branch_droop, glm.normalize(right_world)) * st.q)
                apply_random_rot(st)

            elif ch == "+":
                up_world = glm.vec3(0, 0, 1)
                st.q = glm.normalize(glm.angleAxis(jitter_angle(self.yaw, st), glm.normalize(up_world)) * st.q)

            elif ch == "-":
                up_world = glm.vec3(0, 0, 1)
                st.q = glm.normalize(glm.angleAxis(-jitter_angle(self.yaw, st), glm.normalize(up_world)) * st.q)

            elif ch == "&":
                right_world = glm.mat3_cast(st.q) * glm.vec3(1, 0, 0)
                st.q = glm.normalize(glm.angleAxis(jitter_angle(self.pitch, st), glm.normalize(right_world)) * st.q)

            elif ch == "^":
                right_world = glm.mat3_cast(st.q) * glm.vec3(1, 0, 0)
                st.q = glm.normalize(glm.angleAxis(-jitter_angle(self.pitch, st), glm.normalize(right_world)) * st.q)

            elif ch == "\\":
                fwd_world = glm.mat3_cast(st.q) * glm.vec3(0, 1, 0)
                st.q = glm.normalize(glm.angleAxis(jitter_angle(self.roll, st), glm.normalize(fwd_world)) * st.q)

            elif ch == "/":
                fwd_world = glm.mat3_cast(st.q) * glm.vec3(0, 1, 0)
                st.q = glm.normalize(glm.angleAxis(-jitter_angle(self.roll, st), glm.normalize(fwd_world)) * st.q)

            elif ch == "|":
                up_world = glm.vec3(0, 0, 1)
                st.q = glm.normalize(glm.angleAxis(glm.radians(180.0), glm.normalize(up_world)) * st.q)

        if return_max_height:
            return transforms, colors, max_height
        return transforms, colors

def build_tree_instanced(height=6.0, width=2.0, foliage_cards=750, leaf_color=None):
    objs = []

    trunk_height   = height*0.5
    foliage_height = height*0.75

    # --- trunk (L-system instanced log) ---
    log_mesh, log_mat = _get_shared_log_resources()
    log = LSystemLog(
        target_height=trunk_height* 1.5,
        target_radius=width / 6.0,
        depth=4,
        mesh=log_mesh,
        material=log_mat
    )
    objs.append(log.object)

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
        tilt_deg=20.0,
        base_offset=-(trunk_height * 0.12)
    )

    foliage_obj = InstancedMeshObject(foliage_mesh, foliage_mat, transforms=transforms)
    objs.append(foliage_obj)

    return objs


def build_tree_instanced2(height=6.0, width=2.0, foliage_cards=750, leaf_color=None):
    objs = []

    trunk_height   = height*0.5
    foliage_height = height*0.75

    # --- trunk (L-system instanced log) ---
    log_mesh, log_mat = _get_shared_log_resources()
    log = LSystemLog(
        target_height=trunk_height,
        target_radius=width / 4.0,
        depth=5,
        mesh=log_mesh,
        material=log_mat
    )
    objs.append(log.object)

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
        base_offset=-(trunk_height * 0.12)
    )

    foliage_obj = InstancedMeshObject(foliage_mesh, foliage_mat, transforms=transforms)
    objs.append(foliage_obj)

    return objs
