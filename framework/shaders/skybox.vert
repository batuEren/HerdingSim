#version 430 core

layout (location = 0) in vec3 aPos;

out vec3 vDir;

uniform mat4 view;
uniform mat4 projection;

void main()
{
    mat4 rotView = mat4(mat3(view));

    vDir = aPos;

    vec4 pos = projection * rotView * vec4(aPos, 1.0);
    gl_Position = pos.xyww; // push to far plane
}
