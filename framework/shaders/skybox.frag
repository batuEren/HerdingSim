#version 430 core
out vec4 FragColor;

in vec3 vDir;

uniform float uTime;              // seconds
uniform float dayLength = 120.0;  // seconds per full cycle (tweak)
uniform float starStrength = 1.0; // 0..2
uniform float moonStrength = 0.8; // 0..2
uniform float sunStrength  = 1.2; // 0..3

// --- helpers ---
float hash(vec3 p) {
    // cheap stable hash
    p = fract(p * 0.3183099 + vec3(0.1,0.2,0.3));
    p *= 17.0;
    return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

vec3 tonemap(vec3 c) {
    // simple filmic-ish curve
    c = max(c, 0.0);
    return c / (c + vec3(1.0));
}

void main()
{
    vec3 dir = normalize(vDir);

    // Time -> [0,1)
    float t = fract(uTime / max(dayLength, 1e-3));

    // Sun goes around the sky: midnight at t=0, noon at t=0.5 (you can shift)
    float ang = (t * 6.2831853) - 1.5707963; // shift so sunrise/sunset feel nicer
    vec3 sunDir  = normalize(vec3(cos(ang), sin(ang), 0.25));
    vec3 moonDir = -sunDir;

    // "Sun height" drives day/night blend
    float sunH = clamp(sunDir.y * 0.5 + 0.5, 0.0, 1.0); // 0 night -> 1 day
    float night = 1.0 - sunH;

    // Base gradients
    vec3 zenithDay   = vec3(0.20, 0.45, 0.95);
    vec3 horizonDay  = vec3(0.85, 0.90, 1.00);

    vec3 zenithNight  = vec3(0.02, 0.03, 0.07);
    vec3 horizonNight = vec3(0.05, 0.05, 0.10);

    float up = clamp(dir.y * 0.5 + 0.5, 0.0, 1.0);
    float grad = pow(up, 0.65);

    vec3 dayCol   = mix(horizonDay,  zenithDay,  grad);
    vec3 nightCol = mix(horizonNight, zenithNight, grad);

    // Sunrise/sunset tint near horizon when sun is low
    float sunLow = 1.0 - smoothstep(0.30, 0.60, sunH);          // strong when sunH small
    float nearHorizon = 1.0 - smoothstep(0.05, 0.35, abs(dir.y)); // strongest at horizon
    vec3 sunsetTint = vec3(1.00, 0.35, 0.05);
    dayCol += sunsetTint * sunLow * nearHorizon * 0.35;

    // Sun disc + glow
    float sunDot = max(dot(dir, sunDir), 0.0);
    float sunDisc = smoothstep(0.9994, 0.9999, sunDot); // tiny sharp disc
    float sunGlow = pow(sunDot, 64.0) + 0.35 * pow(sunDot, 8.0);

    // Moon disc + subtle glow (only at night)
    float moonDot = max(dot(dir, moonDir), 0.0);
    float moonDisc = smoothstep(0.9992, 0.99985, moonDot);
    float moonGlow = 0.25 * pow(moonDot, 18.0);

    // Stars: random points on the sphere, fade out near horizon + during day
    float starMask = smoothstep(0.10, 0.55, dir.y * 0.5 + 0.5); // fewer near horizon
    float starField = 0.0;

    // Sample a few "cells" from direction to make sparse stars
    vec3 p = normalize(dir) * 400.0; // scale controls density distribution
    float h = hash(floor(p));
    float star = smoothstep(0.997, 1.0, h); // sparse
    // twinkle
    float tw = 0.6 + 0.4 * sin(uTime * 2.0 + h * 40.0);
    starField = star * tw;

    float starsVis = starStrength * night * starMask;
    vec3 starsCol = vec3(1.0, 1.0, 1.0) * starField * starsVis;

    // Combine
    vec3 col = mix(nightCol, dayCol, sunH);

    col += vec3(1.0, 0.98, 0.90) * sunGlow * sunStrength * sunH;
    col += vec3(1.0, 0.98, 0.88) * sunDisc * 4.0 * sunStrength * sunH;

    col += vec3(0.75, 0.80, 0.95) * (moonGlow + moonDisc * 2.5) * moonStrength * night;

    col += starsCol;

    // Slight overall lift so nights aren't crushed
    col += vec3(0.01, 0.012, 0.02) * night;

    col = tonemap(col);
    col = pow(col, vec3(1.0/2.2)); // gamma

    FragColor = vec4(col, 1.0);
}
