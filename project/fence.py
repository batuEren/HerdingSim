import math
import random

from framework.renderer import *
from framework.shapes import Cylinder, Cone
from framework.objects import MeshObject
from framework.materials import Material
from pyglm import glm

def build_fence(start, end, spacing, height_func,
                pole_height=2.0,
                pole_thickness=0.2,
                rail_height_offsets=(0.7, 1.5)):
    """
    Builds a list of MeshObjects representing a fence between start and end.

    - start, end: glm.vec3 (x, y, z). y is ignored; height_func decides final y.
    - spacing: distance between fence posts in world units.
    - height_func: function (x, z) -> y
    - pole_height: vertical size of each pole
    - pole_thickness: thickness of poles and rails
    - rail_height_offsets: heights (above ground at each pole) where rails run
    """

    objs = []

    # Direction and length in XZ plane
    dir_xz = glm.vec2(end.x - start.x, end.z - start.z)
    length = glm.length(dir_xz)
    if length <= 0.0001:
        return objs

    # Number of segments
    num_segments = max(1, int(length // spacing))
    step = 1.0 / float(num_segments)

    # Re-use meshes and materials
    wood_color = glm.vec4(0.5, 0.3, 0.1, 1.0)

    pole_mesh = Cube(color=wood_color, side_length=1.0)
    pole_mat = Material()

    rail_mesh = Cube(color=wood_color, side_length=1.0)
    rail_mat = pole_mat  # same material

    # Compute all pole positions (on terrain)
    pole_positions = []
    for i in range(num_segments + 1):
        t = i * step
        x = start.x + t * (end.x - start.x)
        z = start.z + t * (end.z - start.z)
        y = height_func(x, z)
        pole_positions.append(glm.vec3(x, y, z))

        # Create pole transform
        pole_transform = glm.mat4(1.0)
        pole_transform = glm.translate(
            pole_transform,
            glm.vec3(x, y + pole_height * 0.5, z)
        )
        pole_transform = glm.scale(
            pole_transform,
            glm.vec3(pole_thickness, pole_height, pole_thickness)
        )

        objs.append(MeshObject(pole_mesh, pole_mat, transform=pole_transform))

    # Create rails between consecutive poles
    for i in range(num_segments):
        p0 = pole_positions[i]
        p1 = pole_positions[i + 1]

        for h_offset in rail_height_offsets:
            # Start & end of this rail, following terrain at both poles
            a = glm.vec3(p0.x, p0.y + h_offset, p0.z)
            b = glm.vec3(p1.x, p1.y + h_offset, p1.z)

            dir_vec = b - a
            seg_len = glm.length(dir_vec)
            if seg_len <= 0.0001:
                continue

            # Local +X points along the segment A -> B
            forward = glm.normalize(dir_vec)  # local X
            up_world = glm.vec3(0.0, 1.0, 0.0)

            # If almost vertical, choose a different world-up to avoid degenerate cross
            if abs(glm.dot(forward, up_world)) > 0.99:
                up_world = glm.vec3(0.0, 0.0, 1.0)

            # Build an orthonormal basis
            right = glm.normalize(glm.cross(up_world, forward))  # perpendicular in XZ-ish
            up = glm.cross(forward, right)

            # midpoint of the rail
            mid = (a + b) * 0.5

            # Orientation matrix: columns are basis vectors
            basis = glm.mat4(1.0)
            basis[0] = glm.vec4(forward, 0.0)  # local X = along fence segment
            basis[1] = glm.vec4(up, 0.0)  # local Y
            basis[2] = glm.vec4(right, 0.0)  # local Z

            rail_transform = glm.mat4(1.0)
            rail_transform = glm.translate(rail_transform, mid)
            rail_transform = rail_transform * basis

            # Scale along local X (forward) to match segment length
            rail_transform = glm.scale(
                rail_transform,
                glm.vec3(seg_len, pole_thickness * 0.5, pole_thickness)
            )

            objs.append(MeshObject(rail_mesh, rail_mat, transform=rail_transform))

    return objs
