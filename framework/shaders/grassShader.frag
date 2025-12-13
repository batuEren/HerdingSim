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

// --- wind uniforms ---
uniform float uTime;
uniform float wind_color_strength = 1.70;
uniform float wind_color_freq = 1.2;          // a bit faster
uniform vec2  wind_color_world_scale = vec2(0.22, 0.17); // larger => more variation

in vec3 frag_normal;
in vec4 frag_color;
in vec4 frag_pos;
in vec2 frag_uv;

#ifdef USE_ALBEDO_TEXTURE
uniform sampler2D albedo_texture_sampler;
uniform float alpha_cutoff = 0.3;
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

    alpha *= tex_color.a;
    if (alpha < alpha_cutoff) discard;

    base_color *= tex_color.rgb;
#endif

    // --- wind shimmer / color modulation (stronger + more organic) ---
    float phase = dot(frag_pos.xz, wind_color_world_scale) + uTime * wind_color_freq;

    // 0..1 wind signal with some "gustiness"
    float w1 = sin(phase);
    float w2 = sin(phase * 1.73 + 1.2);
    float w3 = sin(phase * 0.63 - 0.7);
    float w  = 0.5 + 0.5 * (0.55*w1 + 0.30*w2 + 0.15*w3);  // roughly 0..1

    // Use w to tint: darker in troughs, warmer/brighter in peaks
    vec3 darkTint = vec3(0.92, 0.97, 0.92);   // slightly darker/colder
    vec3 gustTint = vec3(1.10, 1.10, 0.95);   // slightly brighter/yellower

    vec3 windTint = mix(darkTint, gustTint, w);

    // Apply tint strength (0 => no change, 1 => full tint)
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

    out_color = vec4(result, 1.0);
}
