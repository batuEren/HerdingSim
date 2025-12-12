#version 430 core

uniform mat4 view;
uniform int light_count;
uniform vec4 light_position[10];
uniform vec4 light_color[10];

uniform float ambient_strength = 0.2;
uniform float specular_strength = 0.5;
uniform float diffuse_strength = 1.0;
uniform float shininess = 64.0;
uniform vec2 texture_scale;

in vec3 frag_normal;
in vec4 frag_color;
in vec4 frag_pos;
in vec2 frag_uv;

#ifdef USE_ALBEDO_TEXTURE
uniform sampler2D albedo_texture_sampler;
uniform float alpha_cutoff = 0.3;   // tweak 0.2–0.5
#endif

out vec4 out_color;

void main()
{
    vec2 scaled_uv = frag_uv * texture_scale;

    vec3 N = normalize(frag_normal);
    vec3 V = normalize(-frag_pos.xyz);

    vec3 base_color = frag_color.rgb;
    float alpha = frag_color.a;

#ifdef USE_ALBEDO_TEXTURE
    vec4 tex_color = texture(albedo_texture_sampler, scaled_uv);

    // Use texture alpha
    alpha *= tex_color.a;

    // Cutout (kills halo + avoids transparency sorting issues)
    if (alpha < alpha_cutoff) discard;

    base_color *= tex_color.rgb;
#endif

    vec3 result = base_color * ambient_strength;

    for (int lid = 0; lid < light_count; ++lid) {
        vec3 L = normalize(light_position[lid].xyz - frag_pos.xyz);
        vec3 lightCol = light_color[lid].rgb;

        float diff = max(dot(N, L), 0.0);
        vec3 diffuse = diffuse_strength * base_color * diff * lightCol;

        vec3 H = normalize(L + V);
        float spec = pow(max(dot(N, H), 0.0), shininess);
        vec3 specular = specular_strength * spec * lightCol;

        result += diffuse + specular;
    }

    out_color = vec4(result, 1.0);
}
