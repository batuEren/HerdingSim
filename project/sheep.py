import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import Flycamera
from framework.window import *
from framework.renderer import *
from framework.light import *
from framework.shapes import Cube, UVSphere, Quad, Cylinder, Cone
from framework.objects import InstancedMeshObject
from framework.materials import Material

from pyglm import glm
import numpy as np
import random
import math

class Sheep:
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

        body_mesh = UVSphere(1.0, color=glm.vec4(1.0))
        head_mesh = UVSphere(0.6, color=glm.vec4(0.5, 0.5, 0.5, 1.0))
        leg_mesh = Cylinder(radius=0.1, height=0.6, color=glm.vec4(0.3, 0.3, 0.3, 1.0))
        eye_white_mesh = UVSphere(0.12, color=glm.vec4(1.0, 1.0, 1.0, 1.0))
        eye_black_mesh = UVSphere(0.10, color=glm.vec4(0.0, 0.0, 0.0, 1.0))
        ear_mesh = Cone(radius=0.15, height=0.25, segments=4, color=glm.vec4(0.5, 0.5, 0.5, 1.0))
        tail_mesh = UVSphere(0.18, color=glm.vec4(1.0, 1.0, 1.0, 1.0))

        wool_mat = Material()
        head_mat = Material()
        skin_mat = Material()
        eye_white_mat = Material()
        eye_black_mat = Material()

        part_specs = {
            "body": (body_mesh, wool_mat, count, glm.vec4(1.0, 1.0, 1.0, 1.0)),
            "head": (head_mesh, head_mat, count, glm.vec4(0.5, 0.5, 0.5, 1.0)),
            "legs": (leg_mesh, skin_mat, count * 4, glm.vec4(0.3, 0.3, 0.3, 1.0)),
            "eye_white": (eye_white_mesh, eye_white_mat, count * 2, glm.vec4(1.0, 1.0, 1.0, 1.0)),
            "eye_black": (eye_black_mesh, eye_black_mat, count * 2, glm.vec4(0.0, 0.0, 0.0, 1.0)),
            "ears": (ear_mesh, head_mat, count * 2, glm.vec4(0.5, 0.5, 0.5, 1.0)),
            "tail": (tail_mesh, wool_mat, count, glm.vec4(1.0, 1.0, 1.0, 1.0)),
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

    def __init__(self, renderer, height_func, color=glm.vec4(1.0, 1.0, 1.0, 1.0), obstacles=None, flock=None, predators=None, bounds=None):
        self.frames = 0
        self.walker_position = glm.vec3(0.0)
        self.walker_direction = glm.vec3(1.0, 0.0, 0.0)
        self.change_direction_probability = 0.35
        self.walk_speed = 2.0
        self.flee_speed_boost = 2.0
        self.separation_speed_boost = 0.8
        self.separation_speed_radius = 1.5
        self.height_func = height_func
        self.color = color
        self.obstacles = obstacles if obstacles is not None else []
        self.obstacle_avoid_radius = 6.0
        self.obstacle_avoid_strength = 4.0
        self.predators = predators if predators is not None else []
        self.predator_avoid_radius = 18.0
        self.predator_avoid_strength = 8.0
        self.flock = flock if flock is not None else []
        self.neighbor_radius = 10.0
        self.separation_radius = 5.0
        self.cohesion_weight = 0.75
        self.alignment_weight = 0.82
        self.separation_weight = 2.0
        self.bound_box_length = 200
        self.bounds = bounds  # (half_width, half_depth) in world units
        self.bounce_speed_threshold = self.walk_speed * 1.15
        self.bounce_amplitude = 0.15
        self.bounce_frequency = 2.0
        self.bob_phase = 0.0
        self.bob_offset = 0.0
        self.current_speed = 0.0

        if not Sheep._instanced_ready:
            Sheep.init_instancing(renderer, 1)

        self.index = Sheep._next_index
        if self.index >= Sheep._instanced_capacity:
            raise ValueError("Sheep instance capacity exceeded. Call Sheep.init_instancing(renderer, count).")
        Sheep._next_index += 1

        # Body - procedural parts instanced
        self.body_scale = glm.vec3(1.5, 1.5, 1.5) * 0.7
        self.color = color
        Sheep._part_colors["body"][self.index] = self.color
        Sheep._dirty_colors.add("body")

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

        dist = max(abs(self.walker_position.x), abs(self.walker_position.x))

        if dist > self.bound_box_length*0.7:
            steer += glm.normalize(-self.walker_position) * (dist / self.bound_box_length)

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
    
    def _avoid_predators(self):
        steer = glm.vec3(0.0)
        for p in self.predators:
            offset = self.walker_position - p.walker_position
            offset.y = 0.0
            dist = glm.length(offset)
            if dist < 0.0001 or dist > self.predator_avoid_radius:
                continue
            strength = 1.0 - (dist / self.predator_avoid_radius)
            steer += glm.normalize(offset) * strength
        return steer
    
    def _predator_speed_multiplier(self):
        if not self.predators:
            return 1.0

        closest = None
        for p in self.predators:
            offset = p.walker_position - self.walker_position
            offset.y = 0.0
            dist = glm.length(offset)
            if dist < 0.0001:
                continue
            if closest is None or dist < closest:
                closest = dist

        if closest is None or closest > self.predator_avoid_radius:
            return 1.0

        t = 1.0 - (closest / self.predator_avoid_radius)
        return 1.0 + (t * self.flee_speed_boost)
    
    def _separation_speed_multiplier(self):
        if not self.flock:
            return 1.0

        closest = None
        for other in self.flock:
            if other is self:
                continue
            offset = other.walker_position - self.walker_position
            offset.y = 0.0
            dist = glm.length(offset)
            if dist < 0.0001:
                continue
            if closest is None or dist < closest:
                closest = dist

        if closest is None or closest > self.separation_speed_radius:
            return 1.0

        t = 1.0 - (closest / self.separation_speed_radius)
        return 1.0 + (t * self.separation_speed_boost)

    def move_walker(self, delta_time):
        # compute the probability of the character changing directions this frame,
        # given its probability per second, and the time between now and the previous frame
        p_change_direction = 1.0 - glm.pow(glm.clamp(1.0 - self.change_direction_probability, 0.0, 1.0), delta_time)

        if random.random() < p_change_direction:
            axis = glm.vec3(0.0, 1.0, 0.0)
            rot = glm.rotate(glm.mat4(1.0), glm.radians(30), axis)
            self.walker_direction = glm.vec3(rot * glm.vec4(self.walker_direction, 1.0))

            #self.walker_direction = glm.vec3(0.0, 0.0, 0.0)

        avoid = self._avoid_obstacles()
        flock = self._flock()
        predators = self._avoid_predators()
        combined = (avoid * self.obstacle_avoid_strength) + (predators * self.predator_avoid_strength) + flock

        if glm.length(combined) > 0.0001:
            desired = self.walker_direction + combined
            if glm.length(desired) > 0.0001:
                self.walker_direction = glm.normalize(desired)

        # update the character's position. We multiply by delta time to make sure it moves "walk_speed" units forward per second, regardless of framerate.
        speed = self.walk_speed * self._predator_speed_multiplier() * self._separation_speed_multiplier()
        self.current_speed = speed
        self.walker_position += self.walker_direction * speed * delta_time
        if self.bounds is not None:
            half_width, half_depth = self.bounds
            clamped_x = glm.clamp(self.walker_position.x, -half_width, half_width)
            clamped_z = glm.clamp(self.walker_position.z, -half_depth, half_depth)

            if clamped_x != self.walker_position.x:
                self.walker_direction.x = -abs(self.walker_direction.x) if clamped_x >= half_width else abs(self.walker_direction.x)
                self.walker_position.x = clamped_x
            if clamped_z != self.walker_position.z:
                self.walker_direction.z = -abs(self.walker_direction.z) if clamped_z >= half_depth else abs(self.walker_direction.z)
                self.walker_position.z = clamped_z

            if glm.length(self.walker_direction) > 0.0001:
                self.walker_direction = glm.normalize(self.walker_direction)
        self.walker_position.y = self.height_func(self.walker_position.x, self.walker_position.z)
        if speed > self.bounce_speed_threshold:
            self.bob_phase += delta_time * self.bounce_frequency * 2.0 * math.pi
            self.bob_offset = math.sin(self.bob_phase) * self.bounce_amplitude
        else:
            self.bob_phase = 0.0
            self.bob_offset = 0.0
        #print("walked by: " + str(self.walk_speed * delta_time))
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
            glm.translate(self.walker_position + glm.vec3(0.0, self.body_scale.y * 0.5 + self.bob_offset, 0.0))
            * rotation
            * align
            * glm.scale(self.body_scale)
        )

        body_transform = root * glm.scale(glm.vec3(1.0, 0.9, 0.9))
        head_transform = body_transform * glm.translate(glm.vec3(1.2, 0.2, 0.0))

        Sheep._part_transforms["body"][self.index] = body_transform
        Sheep._part_transforms["head"][self.index] = head_transform

        leg_offsets = [
            glm.vec3(0.5, -0.55, 0.4),
            glm.vec3(-0.5, -0.55, 0.4),
            glm.vec3(0.5, -0.55, -0.4),
            glm.vec3(-0.5, -0.55, -0.5),
        ]
        leg_base = self.index * 4
        for i, offset in enumerate(leg_offsets):
            Sheep._part_transforms["legs"][leg_base + i] = body_transform * glm.translate(offset)

        eye_base = self.index * 2
        for i, side in enumerate([-1, 1]):
            eye_transform = head_transform * glm.translate(glm.vec3(0.45, 0.15, 0.2 * side))
            Sheep._part_transforms["eye_white"][eye_base + i] = eye_transform
            Sheep._part_transforms["eye_black"][eye_base + i] = eye_transform * glm.translate(glm.vec3(0.06, 0.0, 0.0))

        ear_base = self.index * 2
        for i, side in enumerate([-1, 1]):
            ear_transform = (
                head_transform
                * glm.translate(glm.vec3(0.0, 0.55, 0.35 * side))
                * glm.rotate(glm.radians(90), glm.vec3(0, 0, 1))
                * glm.scale(glm.vec3(1.0, 0.5, 1.0))
            )
            Sheep._part_transforms["ears"][ear_base + i] = ear_transform

        tail_transform = body_transform * glm.translate(glm.vec3(-1.05, 0.1, 0.0))
        Sheep._part_transforms["tail"][self.index] = tail_transform

        Sheep._dirty_transforms = True


    def animate(self, delta_time):
        self.frames += 1
        self.move_walker(delta_time)
