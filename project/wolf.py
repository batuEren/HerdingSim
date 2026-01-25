import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import Flycamera
from framework.window import *
from framework.renderer import *
from framework.light import *
from framework.shapes import UVSphere, Cylinder, Cone
from framework.objects import InstancedMeshObject
from framework.materials import Material

from pyglm import glm
import random


class Wolf:
    _instanced_ready = False
    _instanced_capacity = 0
    _next_index = 0
    _renderer = None
    _parts = {}
    _part_transforms = {}
    _part_colors = {}
    _dirty_transforms = False
    _dirty_colors = set()

    @classmethod
    def init_instancing(cls, renderer, count):
        if cls._instanced_ready:
            return

        cls._renderer = renderer
        cls._instanced_capacity = count
        cls._next_index = 0

        def _identities(n):
            return [glm.mat4(1.0) for _ in range(n)]

        def _colors(color, n):
            return [color for _ in range(n)]

        body_mesh = UVSphere(1.0, color=glm.vec4(0.3, 0.3, 0.3, 1.0))
        head_mesh = UVSphere(0.6, color=glm.vec4(0.35, 0.35, 0.35, 1.0))
        leg_mesh = Cylinder(radius=0.1, height=0.75, color=glm.vec4(0.25, 0.25, 0.25, 1.0))
        eye_white_mesh = UVSphere(0.12, color=glm.vec4(1.0, 1.0, 1.0, 1.0))
        eye_black_mesh = UVSphere(0.09, color=glm.vec4(0.0, 0.0, 0.0, 1.0))
        ear_mesh = Cone(radius=0.35, height=0.5, segments=4, color=glm.vec4(0.3, 0.3, 0.3, 1.0))
        tail_cone_mesh = Cone(radius=0.4, height=0.25, segments=8, color=glm.vec4(0.45, 0.45, 0.45, 1.0))
        tail_cyl_mesh = Cylinder(radius=0.2, height=0.8, color=glm.vec4(0.45, 0.45, 0.45, 1.0))
        snout_mesh = Cone(radius=0.35, height=0.45, segments=8, color=glm.vec4(0.4, 0.4, 0.4, 1.0))
        nose_mesh = UVSphere(0.13, color=glm.vec4(0.1, 0.1, 0.1, 1.0))

        fur_mat = Material()
        eye_white_mat = Material()
        eye_black_mat = Material()

        part_specs = {
            "body": (body_mesh, fur_mat, count, glm.vec4(0.3, 0.3, 0.3, 1.0)),
            "head": (head_mesh, fur_mat, count, glm.vec4(0.35, 0.35, 0.35, 1.0)),
            "legs": (leg_mesh, fur_mat, count * 4, glm.vec4(0.25, 0.25, 0.25, 1.0)),
            "tail_cone": (tail_cone_mesh, fur_mat, count, glm.vec4(0.45, 0.45, 0.45, 1.0)),
            "tail_cyl": (tail_cyl_mesh, fur_mat, count, glm.vec4(0.45, 0.45, 0.45, 1.0)),
            "eye_white": (eye_white_mesh, eye_white_mat, count * 2, glm.vec4(1.0, 1.0, 1.0, 1.0)),
            "eye_black": (eye_black_mesh, eye_black_mat, count * 2, glm.vec4(0.0, 0.0, 0.0, 1.0)),
            "ears": (ear_mesh, fur_mat, count * 2, glm.vec4(0.3, 0.3, 0.3, 1.0)),
            "snout": (snout_mesh, fur_mat, count, glm.vec4(0.4, 0.4, 0.4, 1.0)),
            "nose": (nose_mesh, fur_mat, count, glm.vec4(0.1, 0.1, 0.1, 1.0)),
        }

        for part, (mesh, mat, amount, color) in part_specs.items():
            transforms = _identities(amount)
            colors = _colors(color, amount)
            instanced_obj = InstancedMeshObject(mesh, mat, transforms, colors)
            renderer.addObject(instanced_obj)
            cls._parts[part] = instanced_obj
            cls._part_transforms[part] = transforms
            cls._part_colors[part] = colors

        cls._instanced_ready = True

    @classmethod
    def flush_instanced(cls):
        if not cls._instanced_ready:
            return

        if cls._dirty_transforms:
            for part, obj in cls._parts.items():
                obj.update_transforms(cls._part_transforms[part])
            cls._dirty_transforms = False

        if cls._dirty_colors:
            for part in cls._dirty_colors:
                obj = cls._parts.get(part)
                if obj is not None:
                    obj.update_colors(cls._part_colors[part])
            cls._dirty_colors = set()

    def __init__(self, renderer, height_func, color=glm.vec4(0.2, 0.2, 0.2, 1.0), obstacles=None, flock=None, prey=None):
        self.frames = 0
        self.walker_position = glm.vec3(0.0)
        self.walker_direction = glm.vec3(1.0, 0.0, 0.0)
        self.change_direction_probability = 0.15
        self.walk_speed = 2.5
        self.height_func = height_func
        self.color = color
        self.obstacles = obstacles if obstacles is not None else []
        self.obstacle_avoid_radius = 7.0
        self.obstacle_avoid_strength = 4.0
        self.flock = flock if flock is not None else []
        self.prey = prey if prey is not None else []
        self.neighbor_radius = 12.0
        self.separation_radius = 5.0
        self.cohesion_weight = 0.5
        self.alignment_weight = 0.7
        self.separation_weight = 1.2
        self.chase_radius = 40.0
        self.chase_weight = 2.5

        if not Wolf._instanced_ready:
            Wolf.init_instancing(renderer, 1)

        self.index = Wolf._next_index
        if self.index >= Wolf._instanced_capacity:
            raise ValueError("Wolf instance capacity exceeded. Call Wolf.init_instancing(renderer, count).")
        Wolf._next_index += 1

        self.body_scale = glm.vec3(1.6, 1.6, 1.6) * 0.5
        self.color = color

        fur_color = glm.vec4(color.x, color.y, color.z, color.w)
        tail_color = glm.vec4(
            min(color.x + 0.15, 1.0),
            min(color.y + 0.15, 1.0),
            min(color.z + 0.15, 1.0),
            color.w,
        )
        leg_color = glm.vec4(
            max(color.x - 0.05, 0.0),
            max(color.y - 0.05, 0.0),
            max(color.z - 0.05, 0.0),
            color.w,
        )
        snout_color = glm.vec4(
            min(color.x + 0.1, 1.0),
            min(color.y + 0.1, 1.0),
            min(color.z + 0.1, 1.0),
            color.w,
        )

        Wolf._part_colors["body"][self.index] = fur_color
        Wolf._part_colors["head"][self.index] = fur_color
        Wolf._part_colors["tail_cone"][self.index] = tail_color
        Wolf._part_colors["tail_cyl"][self.index] = tail_color
        Wolf._part_colors["snout"][self.index] = snout_color

        leg_base = self.index * 4
        for i in range(4):
            Wolf._part_colors["legs"][leg_base + i] = leg_color

        ear_base = self.index * 2
        for i in range(2):
            Wolf._part_colors["ears"][ear_base + i] = fur_color

        Wolf._dirty_colors.update(["body", "head", "tail_cone", "tail_cyl", "snout", "legs", "ears"])

    def _avoid_obstacles(self):
        steer = glm.vec3(0.0)
        for o in self.obstacles:
            offset = self.walker_position - o
            offset.y = 0.0
            dist = glm.length(offset)
            if dist < 0.0001 or dist > self.obstacle_avoid_radius:
                continue
            strength = 1.0 - (dist / self.obstacle_avoid_radius)
            steer += glm.normalize(offset) * strength
        return steer

    def _flock(self):
        if not self.flock:
            return glm.vec3(0.0)

        center = glm.vec3(0.0)
        avg_dir = glm.vec3(0.0)
        separation = glm.vec3(0.0)
        neighbors = 0

        for other in self.flock:
            if other is self:
                continue
            offset = other.walker_position - self.walker_position
            offset.y = 0.0
            dist = glm.length(offset)
            if dist < 0.0001 or dist > self.neighbor_radius:
                continue
            center += other.walker_position
            avg_dir += other.walker_direction
            neighbors += 1

            if dist < self.separation_radius:
                separation -= glm.normalize(offset) * (1.0 - (dist / self.separation_radius))

        if neighbors == 0:
            return glm.vec3(0.0)

        center /= neighbors
        cohesion = center - self.walker_position
        cohesion.y = 0.0
        if glm.length(cohesion) > 0.0001:
            cohesion = glm.normalize(cohesion)

        if glm.length(avg_dir) > 0.0001:
            avg_dir = glm.normalize(avg_dir)

        steer = (cohesion * self.cohesion_weight) + (avg_dir * self.alignment_weight) + (separation * self.separation_weight)
        return steer

    def _chase_prey(self):
        if not self.prey:
            return glm.vec3(0.0)

        closest = None
        closest_dist = self.chase_radius
        for s in self.prey:
            offset = s.walker_position - self.walker_position
            offset.y = 0.0
            dist = glm.length(offset)
            if dist < closest_dist:
                closest_dist = dist
                closest = offset

        if closest is None or glm.length(closest) < 0.0001:
            return glm.vec3(0.0)

        return glm.normalize(closest)

    def move_walker(self, delta_time):
        p_change_direction = 1.0 - glm.pow(glm.clamp(1.0 - self.change_direction_probability, 0.0, 1.0), delta_time)

        if random.random() < p_change_direction:
            axis = glm.vec3(0.0, 1.0, 0.0)
            rot = glm.rotate(glm.mat4(1.0), glm.radians(20), axis)
            self.walker_direction = glm.vec3(rot * glm.vec4(self.walker_direction, 1.0))

        avoid = self._avoid_obstacles()
        flock = self._flock()
        chase = self._chase_prey()
        combined = (avoid * self.obstacle_avoid_strength) + flock + (chase * self.chase_weight)

        if glm.length(combined) > 0.0001:
            desired = self.walker_direction + combined
            if glm.length(desired) > 0.0001:
                self.walker_direction = glm.normalize(desired)

        self.walker_position += self.walker_direction * self.walk_speed * delta_time
        self.walker_position.y = self.height_func(self.walker_position.x, self.walker_position.z)
        self.update_walker_geometry()

    def update_walker_geometry(self):
        forward = glm.vec3(self.walker_direction.x, 0.0, self.walker_direction.z)
        if glm.length(forward) < 1e-4:
            forward = glm.vec3(1.0, 0.0, 0.0)
        forward = glm.normalize(forward)
        rotation = glm.mat4_cast(glm.quatLookAt(forward, glm.vec3(0.0, 1.0, 0.0)))
        align = (
            glm.rotate(glm.mat4(1.0), glm.radians(-90.0), glm.vec3(0.0, 1.0, 0.0))
            * glm.rotate(glm.mat4(1.0), glm.radians(180.0), glm.vec3(0.0, 1.0, 0.0))
        )
        root = (
            glm.translate(self.walker_position + glm.vec3(0.0, self.body_scale.y * 0.5, 0.0))
            * rotation
            * align
            * glm.scale(self.body_scale)
        )

        body_transform = root * glm.scale(glm.vec3(1.3, 0.7, 0.7))
        head_transform = body_transform * glm.translate(glm.vec3(1.05, 0.17, 0.0))

        Wolf._part_transforms["body"][self.index] = body_transform
        Wolf._part_transforms["head"][self.index] = head_transform

        leg_offsets = [
            glm.vec3(0.5, -1.0, 0.4),
            glm.vec3(-0.5, -1.0, 0.4),
            glm.vec3(0.5, -1.0, -0.4),
            glm.vec3(-0.5, -1.0, -0.4),
        ]
        leg_base = self.index * 4
        for i, offset in enumerate(leg_offsets):
            Wolf._part_transforms["legs"][leg_base + i] = body_transform * glm.translate(offset)

        tail_cone_transform = (
            body_transform
            * glm.translate(glm.vec3(-0.85, 0.1, 0.0))
            * glm.rotate(glm.radians(90), glm.vec3(0, 0, 1))
            * glm.rotate(glm.radians(-20), glm.vec3(0, 0, 1))
        )
        Wolf._part_transforms["tail_cone"][self.index] = tail_cone_transform

        tail_cyl_transform = (
            tail_cone_transform
            * glm.translate(glm.vec3(-0.3, 0.1, 0.0))
            * glm.rotate(glm.radians(-90), glm.vec3(0, 0, 1))
            * glm.rotate(glm.radians(-15), glm.vec3(0, 0, 1))
        )
        Wolf._part_transforms["tail_cyl"][self.index] = tail_cyl_transform

        eye_base = self.index * 2
        for i, side in enumerate([-1, 1]):
            eye_transform = head_transform * glm.translate(glm.vec3(0.45, 0.15, 0.2 * side))
            Wolf._part_transforms["eye_white"][eye_base + i] = eye_transform
            Wolf._part_transforms["eye_black"][eye_base + i] = eye_transform * glm.translate(glm.vec3(0.05, 0.0, 0.0))

        ear_base = self.index * 2
        for i, side in enumerate([-1, 1]):
            ear_transform = (
                head_transform
                * glm.translate(glm.vec3(0.0, 0.45, 0.25 * side))
                * glm.rotate(glm.radians(90), glm.vec3(0, 0, 1))
            )
            Wolf._part_transforms["ears"][ear_base + i] = ear_transform

        snout_transform = (
            head_transform
            * glm.translate(glm.vec3(0.6, -0.0, 0.0))
            * glm.rotate(glm.radians(-90), glm.vec3(0, 0, 1))
            * glm.scale(glm.vec3(1.0, 1.2, 1.0))
        )
        Wolf._part_transforms["snout"][self.index] = snout_transform

        nose_transform = head_transform * glm.translate(glm.vec3(0.6 + 0.225 - 0.04, -0.05, 0.0))
        Wolf._part_transforms["nose"][self.index] = nose_transform

        Wolf._dirty_transforms = True

    def animate(self, delta_time):
        self.frames += 1
        self.move_walker(delta_time)
