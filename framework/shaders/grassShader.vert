#version 430 core

// ---- per-vertex attributes ----
// Adjust locations if your engine uses different ones.
layout(location = 0) in vec4 aPos;     // from Shape.vertices (vec4)
layout(location = 1) in vec3 aNormal;  // from Shape.normals  (vec3)
layout(location = 2) in vec4 aColor;   // from Shape.colors   (vec4)
layout(location = 3) in vec2 aUV;      // from Shape.uvs      (vec2)

// ---- per-instance matrix ----
// Typical instancing: mat4 occupies 4 consecutive attribute locations.
layout(location = 4) in mat4 instance_matrix;

// ---- camera matrices ----
uniform mat4 view;
uniform mat4 projection;

// ---- wind uniforms ----
uniform float uTime;
uniform float wind_strength = 0.10;        // world units (try 0.03..0.12)
uniform float wind_freq = 1.6;             // speed
uniform vec2  wind_dir = vec2(1.0, 0.3);   // direction in XZ
uniform vec2  wind_world_scale = vec2(0.12, 0.10); // spatial variation
uniform float grass_height = 0.7;          // MUST match Grass(height=...)

out vec3 frag_normal;
out vec4 frag_color;
out vec4 frag_pos;
out vec2 frag_uv;

void main()
{
    // Local -> World (instance)
    vec4 world = instance_matrix * aPos;

    // --- wind sway ---
    // Bend factor: 0 at base, 1 at tip (your grass mesh has y in [0..height])
    float bend = clamp(aPos.y / grass_height, 0.0, 1.0);
    bend = bend * bend; // keep base more anchored

    // Use world position so nearby blades move similarly, but not identical
    float phase = dot(world.xz, wind_world_scale) + uTime * wind_freq;

    // "gusty" smooth wind signal
    float w1 = sin(phase);
    float w2 = sin(phase * 1.73 + 1.2);
    float w3 = sin(phase * 0.63 - 0.7);
    float w  = (0.55*w1 + 0.30*w2 + 0.15*w3);

    vec2 dir2 = normalize(wind_dir);
    vec3 dir = vec3(dir2.x, 0.0, dir2.y);

    world.xyz += dir * (w * wind_strength * bend);

    // Outputs
    frag_pos = world;

    // If you want grass normals always up, force it here:
    // frag_normal = vec3(0.0, 1.0, 0.0);
    // Otherwise transform the provided normal (better if you ever change normals):
    frag_normal = normalize(mat3(instance_matrix) * aNormal);

    frag_color = aColor;
    frag_uv = aUV;

    gl_Position = projection * view * world;
}
