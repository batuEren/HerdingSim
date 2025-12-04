#version 430 core

in vec3 frag_normal;
in vec4 frag_color;
in vec4 frag_pos;
in vec2 frag_uv;

out vec4 out_color;

void main()
{
    vec4 stripe_color = frag_color;

    vec2 frac_pos = vec2(fract(frag_pos.x), fract(frag_pos.z));

    if (max(frac_pos.x, frac_pos.y) > 0.98 || min(frac_pos.x, frac_pos.y) < 0.02)
        stripe_color = vec4(0.0, 0.0, 0.0, 1.0);

    out_color = stripe_color;
}
