#version 430 core

uniform mat4 view;
uniform mat4 projection;
uniform mat4 model;

layout(location = 0) in vec4 in_position;
layout(location = 1) in vec3 in_normal;
layout(location = 2) in vec4 in_color;
layout(location = 3) in vec2 in_uv;


#ifdef INSTANCED
layout(location = 4) in mat4 in_instance_model;
layout(location = 8) in vec4 in_instance_color;
#endif

out vec3 frag_normal;
out vec4 frag_color;
out vec4 frag_pos;
out vec2 frag_uv;

void main()
{
    mat4 M;
    vec4 base_color;

#ifdef INSTANCED
    M = model * in_instance_model;
    base_color = in_instance_color;
#else
    M = model;
    base_color = in_color;
#endif

    gl_Position = projection * view * M * in_position;
    frag_pos = M * in_position;

    mat4 normal_matrix = transpose(inverse(M));
    frag_normal = normalize(vec3(normal_matrix * vec4(in_normal, 0.0)));

    frag_color = base_color;
    frag_uv = in_uv;
}
