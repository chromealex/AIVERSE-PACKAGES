# terraweave-rocks

Install into a project:

```sh
python3 tools/pkg/aiverse_pkg.py add terraweave-rocks --project <project>
```

Models go to `<project>/models/terraweave/rocks`. The package depends on
`terrain-pbr`; `aiverse_pkg.py add` installs it too (engine 3.1.0+),
because the models use its textures (`../../../materials/terrain/textures/`) instead of carrying copies.

Each model is a `.gltf` + `.bin` with three LOD meshes in `extras.rtsLods`; the engine switches them by
screen size. `catalog.json` lists the models with their generator seeds and triangle counts.

Made by the engine tool `aiverse_terraweave_rocks` (seed 42), MIT licence like the engine.
