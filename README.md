# Hermopolis — Interactive Learning Platform

A SvelteKit web app that hosts interactive, canvas-driven programming courses. Modules are ported from self-contained HTML references using an automated conversion script.

## Courses

### Game Development Fundamentals
*From Pixels to Play* — 12 modules covering the full game dev stack in Python.

| # | Title | Status |
|---|-------|--------|
| 01 | Foundations of 2D Game Development | ✅ Available |
| 02 | The Rendering Pipeline | ✅ Available |
| 03 | Coordinate Systems & Transformations | ✅ Available |
| 04 | Introduction to GPU Rendering | ✅ Available |
| 05–12 | … | 🔒 Coming Soon |

### Animation Fundamentals
*Theory + Practice* — 10 modules covering motion, principles, and visual storytelling.

| # | Title | Status |
|---|-------|--------|
| 01 | The Language of Motion | ✅ Available |
| 02 | Timing & Spacing | ✅ Available |
| 03 | The 12 Principles | ✅ Available |
| 04–10 | … | 🔒 Coming Soon |

## Development

```sh
bun install
bun run dev
```

## Adding a New Module

Use the automated converter to port a legacy HTML module into a Svelte component:

```sh
python3 scripts/convert_module.py <input.html> <src/lib/modules/<course>/ModuleXX.svelte>
```

Then:
1. Set the module `status` to `'available'` in `src/lib/data/courses.ts`
2. Import and register it in the course's `[module]/+page.svelte`

## Tech Stack

- **SvelteKit** with TypeScript
- **Bun** as package manager / runtime
- **Vanilla CSS** — no framework
- **HTML Canvas** for all interactive demos
