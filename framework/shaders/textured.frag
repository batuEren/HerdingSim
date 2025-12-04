#version 430 core

uniform mat4 view;
uniform int  light_count;
uniform vec4 light_position[10];
uniform vec4 light_color[10];

uniform sampler2D texture_sampler;
uniform bool use_texture;
uniform vec2 texture_scale;

in vec3 frag_normal;
in vec4 frag_color;
in vec4 frag_pos;
in vec2 frag_uv;

out vec4 out_color;

void main()
{
    vec4 base_color = frag_color;

    // If texture is enabled, sample it with scaled UVs
    if (use_texture) {
        vec2 scaled_uv = frag_uv * texture_scale;
        vec4 tex_color = texture(texture_sampler, scaled_uv);
        base_color = tex_color;
    }

    // Simple Phong lighting
    vec3 result = base_color.rgb * 0.25; // ambient

    for (int lid = 0; lid < light_count; ++lid) {
        vec3 light_dir = normalize(light_position[lid].xyz - frag_pos.xyz);
        float dotNL = max(0.0, dot(light_dir, normalize(frag_normal)));
        vec3 diffuse = base_color.rgb * dotNL * light_color[lid].rgb;

        vec3 reflection = reflect(-light_dir, normalize(frag_normal));
        vec3 eye_dir = normalize(-frag_pos.xyz);
        float spec = pow(max(dot(reflection, eye_dir), 0.0), 32.0);
        vec3 specular = light_color[lid].rgb * vec3(0.1) * spec;

        result += diffuse + specular;
    }

    out_color = vec4(clamp(result, 0.0, 1.0), 1.0);
}
