import math

from framework.renderer import *
from framework.shapes import Cylinder, Cone
from framework.objects import MeshObject
from framework.materials import Material
from pyglm import glm

def build_tree(position = glm.vec3(0.0, 0., 0.0), height = 4, width = 4, segments= 4): # return tree obj(s)
    objs = []

    log_mesh = Cylinder(radius= width/4.0, height = height/3.0, color=glm.vec4(0.8, 0.5, 0.3, 1.0))
    log_mat = Material()
    log_transform = glm.translate(position) * glm.translate(glm.vec3(0.0, height * 0.33, 0.0))
    log_obj = MeshObject(log_mesh, log_mat, transform=log_transform)

    objs.append(log_obj)

    for i in range(1, segments+1):
        cone_mesh = Cone(color=glm.vec4(0.2, 0.9, 0.2, 1.0), radius=width/max(1, math.log(i)), height=height*0.66 / segments)
        cone_transform = glm.translate(position) * glm.translate(glm.vec3(0.0, height*0.33 + (i*height*0.5/segments), 0.0))
        cone_mat = Material()
        cone_obj = MeshObject(cone_mesh, cone_mat, transform=cone_transform)
        objs.append(cone_obj)

    #MeshObject(mesh=log_mesh, material=cube_mat, transform=cube_transform)
    #floor_obj.transform = glm.rotate(glm.radians(-90), glm.vec3(1, 0, 0))

    return objs