import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import Flycamera
from framework.window import *
from framework.renderer import *
from framework.light import *
from framework.shapes import UVSphere
from framework.objects import MeshObject
from framework.materials import Material

from pyglm import glm
import random


class Wolf:
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

        self.body_scale = glm.vec3(1.8, 1.8, 1.8)
        body_shape = UVSphere(color=self.color)
        body_mat = Material()
        self.body = MeshObject(body_shape, body_mat)
        renderer.addObject(self.body)

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
        self.body.transform = glm.translate(self.walker_position + glm.vec3(0.0, self.body_scale.y * 0.5, 0.0)) * glm.scale(self.body_scale)

    def animate(self, delta_time):
        self.frames += 1
        self.move_walker(delta_time)
