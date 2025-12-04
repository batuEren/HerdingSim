import math
import random

from framework.renderer import *
from framework.shapes import Cylinder, Cone
from framework.objects import MeshObject
from framework.materials import Material
from pyglm import glm


def build_tree(position = glm.vec3(0.0, 0., 0.0), height = 4, width = 4, segments= 4):
    objs = []

    trunk_height   = height / 5.0
    foliage_height = height - trunk_height

    log_mesh = Cylinder(
        radius = width / 4.0,
        height = trunk_height,
        color  = glm.vec4(0.8, 0.5, 0.3, 1.0)
    )
    log_mat = Material()

    log_transform = glm.translate(position + glm.vec3(0.0, trunk_height * 0.5, 0.0))
    log_obj = MeshObject(log_mesh, log_mat, transform=log_transform)
    objs.append(log_obj)

    per_segment = foliage_height / float(segments)

    for i in range(segments):
        cone_height = per_segment
        cone_radius = width / max(1.0, math.log(i + 2))  # avoid log(1)=0

        colorRand = random.random()

        cone_mesh = Cone(
            color  = glm.vec4(0.2+0.4*colorRand, 0.8+0.2*colorRand, 0.2+0.05*colorRand, 1.0),
            radius = cone_radius,
            height = cone_height
        )
        cone_mat = Material()

        cone_center_y = trunk_height + cone_height*0.7 * (0.5 + i)

        cone_transform = glm.translate(position + glm.vec3(0.0, cone_center_y, 0.0))
        cone_obj = MeshObject(cone_mesh, cone_mat, transform=cone_transform)
        objs.append(cone_obj)

    return objs
