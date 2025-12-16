# Herding Simulator

![Herding Simulator](screenshot.png)

**Herding Simulator** is a real-time simulation environment built using **OpenGL** for rendering and **PyGLM** for mathematics and transformations. The project currently focuses on constructing a performant and extensible **procedural environment** that will later support large-scale agent-based simulations.

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

## Planned Work

- Agent-based herding and crowd dynamics  
- Environment-aware agent interaction  
- Scalability testing with large populations  

---

The project currently serves as a **graphics- and performance-oriented sandbox**, designed to support future work on collective behavior without architectural rewrites.
