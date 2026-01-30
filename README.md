# Herding Simulator

![Herding Simulator](screenshot.png)

**Herding Simulator** is a real-time simulation environment built using **OpenGL** for rendering and **PyGLM** for mathematics and transformations. The project combines a procedural environment with emerging **agent behavior** for wildlife dynamics.

## Environment & Rendering

- **Procedural terrain**  
  The terrain is generated using smooth trigonometric height functions (sine / cosine blends), producing continuous hills and valleys without relying on heightmaps. This allows cheap evaluation, infinite tiling, and easy parameterization.

- **Instanced grass rendering**  
  Grass is rendered using GPU instancing, allowing thousands of blades to be drawn efficiently. Randomized transforms (scale, rotation, color variation) are applied per instance to break repetition while keeping draw calls minimal.

- **Double-instanced trees**  
  Trees use a two-level instancing approach:
  - Tree placement is instanced across the terrain  
  - Foliage cards are instanced again within each tree  
  This significantly reduces CPU overhead while enabling dense forests with detailed silhouettes.

- **Wind-animated foliage shaders**  
  Custom vertex shaders animate grass and tree foliage using time-based sine and cosine functions. Wind strength and frequency vary spatially, creating subtle, non-uniform motion that avoids a synchronized look.

## Agents & Behavior

- **Sheep flocking and evasion**  
  Sheep flock together and will run away from nearby wolves.

- **Wolf pursuit**  
  Wolves actively chase sheep when in range.

## Seasons

![Season Change](seasonChange.gif)

- **Season controls**  
  Two buttons step seasons; `1` moves backward and `2` moves forward in time.

- **Seasonal visuals**  
  As seasons change, leaf and grass colors shift, and in winter leaves fall off.

## L-System Tree Logs

Logs are generated using a 3D L-system with the following rule set:

```
axiom = "A"
rules = {
    "A": "F[+B][-B][\\B][/B][&B][^B]GGA",
    "B": "F[+F]F[-F]F[\\F]F[/F]"
}
```

Legend: `+ - ^` are rotations, `G` moves forward, `F` moves forward while drawing a cylinder.


