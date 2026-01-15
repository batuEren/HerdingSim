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
    def __init__(self, renderer, height_func, color=glm.vec4(1.0, 1.0, 1.0, 1.0), obstacles=None):
        self.frames = 0
        self.walker_position = glm.vec3(0.0)
        self.walker_direction = glm.vec3(1.0, 0.0, 0.0)
        self.change_direction_probability = 0.5
        self.walk_speed = 4.0
        self.height_func = height_func
        self.color = color
        self.obstacles = obstacles if obstacles is not None else []
        self.obstacle_avoid_radius = 6.0
        self.obstacle_avoid_strength = 4.0

        # Body - To Do - Cube for now
        self.body_scale = glm.vec3(2.0, 2.0, 2.0)
        body_shape = Cube(color=self.color)
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

    def move_walker(self, delta_time):
        # compute the probability of the character changing directions this frame,
        # given its probability per second, and the time between now and the previous frame
        p_change_direction = 1.0 - glm.pow(glm.clamp(1.0 - self.change_direction_probability, 0.0, 1.0), delta_time)

        if random.random() < p_change_direction:
            axis = glm.vec3(0.0, 1.0, 0.0)
            rot = glm.rotate(glm.mat4(1.0), glm.radians(50), axis)
            self.walker_direction = glm.vec3(rot * glm.vec4(self.walker_direction, 1.0))

            #self.walker_direction = glm.vec3(0.0, 0.0, 0.0)

        avoid = self._avoid_obstacles()
        if glm.length(avoid) > 0.0001:
            desired = self.walker_direction + (avoid * self.obstacle_avoid_strength)
            if glm.length(desired) > 0.0001:
                self.walker_direction = glm.normalize(desired)

        # update the character's position. We multiply by delta time to make sure it moves "walk_speed" units forward per second, regardless of framerate.
        self.walker_position += self.walker_direction * self.walk_speed * delta_time
        self.walker_position.y = self.height_func(self.walker_position.x, self.walker_position.z)
        #print("walked by: " + str(self.walk_speed * delta_time))
        self.update_walker_geometry()

    def update_walker_geometry(self):
        self.body.transform = glm.translate(self.walker_position + glm.vec3(0.0, self.body_scale.y * 0.5, 0.0)) * glm.scale(self.body_scale)


    def animate(self, delta_time):
        self.frames += 1
        self.move_walker(delta_time)
