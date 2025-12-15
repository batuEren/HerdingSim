#version 430 core

uniform mat4 view;
uniform int light_count;
uniform vec4 light_position[10];
uniform vec4 light_color[10];

uniform float ambient_strength = 0.2;
uniform float specular_strength = 0.1;
uniform float diffuse_strength = 1.0;
uniform float shininess = 64.0;
uniform vec2 texture_scale;

// --- wind uniforms ---
uniform float uTime;
uniform float wind_color_strength = 1.70;
uniform float wind_color_freq = 1.2;
uniform vec2  wind_color_world_scale = vec2(0.22, 0.17);

in vec3 frag_normal;
in vec4 frag_color;
in vec4 frag_pos;
in vec2 frag_uv;

#ifdef USE_ALBEDO_TEXTURE
uniform sampler2D albedo_texture_sampler;
uniform float alpha_cutoff = 0.65;
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
    vec4 tex = texture(albedo_texture_sampler, scaled_uv);

    // Kill fully transparent texels early (avoids mipmap fringe)
    if (tex.a <= 0.001)
        discard;

    // Fix RGB fringe from transparent pixels (alpha bleed issue)
    tex.rgb /= max(tex.a, 1e-4);

    alpha *= tex.a;
    if (alpha < alpha_cutoff)
        discard;

    base_color *= tex.rgb;
#endif

    // --- wind shimmer / color modulation ---
    float phase = dot(frag_pos.xz, wind_color_world_scale) + uTime * wind_color_freq;

    float w1 = sin(phase);
    float w2 = sin(phase * 1.73 + 1.2);
    float w3 = sin(phase * 0.63 - 0.7);
    float w  = 0.5 + 0.5 * (0.55*w1 + 0.30*w2 + 0.15*w3);

    vec3 darkTint = vec3(0.92, 0.97, 0.92);
    vec3 gustTint = vec3(1.10, 1.10, 0.95);
    vec3 windTint = mix(darkTint, gustTint, w);

    base_color = mix(base_color, base_color * windTint, wind_color_strength);

    // Lighting
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

    out_color = vec4(result, alpha); // <-- important
}
