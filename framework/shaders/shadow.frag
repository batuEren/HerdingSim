#version 430 core

in vec4 frag_color;
in vec2 frag_uv;

out vec4 out_color;

void main()
{
    vec2 p = frag_uv - vec2(0.5);
    float d = length(p * 2.0);

    float alpha = 1.0 - smoothstep(0.4, 1.0, d);
    alpha *= frag_color.a;

    out_color = vec4(frag_color.rgb, alpha);
}
