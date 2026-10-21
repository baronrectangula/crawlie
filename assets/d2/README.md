# D2 diagrams

D2 sources live here; generated SVGs live in `../diagrams/`. Only standard D2
shapes and native theme support are used. No custom builder is required.

Create `assets/d2/example.d2`, import the shared palette, and use its classes:

```d2
...@palette

direction: down
input: Input {class: block}
output: Output {class: block}
input -> output: {class: flow}
```

Render it directly:

```sh
d2 assets/d2/example.d2 assets/diagrams/example.svg
```

Use `class: [block; extension]` for a dashed extension point and
`class: [block; message-interface]` for a parallelogram representing message input
and output. Interfaces describe communication contracts; they do not imply a
queue, broker, separate process, or particular transport. Edit the D2 source and
regenerate the SVG; do not edit the generated file by hand.

## Palette and viewing

`palette.d2` provides light and dark theme overrides, bold monospace blocks,
square corners, and 3 px outlines. Colors follow D2's native theme assignments;
avoid fixed fill or text colors if they should adapt between themes.

The generated SVG responds to `prefers-color-scheme` without JavaScript. Open it
in a browser and switch the browser or system color preference to inspect both
modes. Some raster converters ignore dark-mode media queries or embedded fonts.
