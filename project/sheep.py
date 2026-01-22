import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import Flycamera
from framework.window import *
from framework.renderer import *
from framework.light import *
from framework.shapes import Cube, UVSphere, Quad
from framework.objects import MeshObject, InstancedMeshObject
from framework.materials import Material

from pyglm import glm
import numpy as np
import random

class Sheep:
    def __init__(self, renderer, height_func, color=glm.vec4(1.0, 1.0, 1.0, 1.0), obstacles=None, flock=None, predators=None):
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
        self.separation_radius = 4.0
        self.cohesion_weight = 0.8
        self.alignment_weight = 0.85
        self.separation_weight = 1.8

        # Body - To Do - Cube for now
        self.body_scale = glm.vec3(1.5, 1.5, 1.5)
        body_shape = UVSphere(color=self.color)
        body_mat   = Material()
        self.body  = MeshObject(body_shape, body_mat)
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
        self.walker_position += self.walker_direction * speed * delta_time
        self.walker_position.y = self.height_func(self.walker_position.x, self.walker_position.z)
        #print("walked by: " + str(self.walk_speed * delta_time))
        self.update_walker_geometry()

    def update_walker_geometry(self):
        self.body.transform = glm.translate(self.walker_position + glm.vec3(0.0, self.body_scale.y * 0.5, 0.0)) * glm.scale(self.body_scale)


    def animate(self, delta_time):
        self.frames += 1
        self.move_walker(delta_time)
