# Design system

## Direction

`optical-design` uses the visual language of a precise optical section drawing: controlled

curves, a shared axis, and a single point where the work resolves. The identity should feel
at home beside engineering documentation while remaining clear to a reader opening the
repository for the first time.

The mark shows three symbolic rays crossing a biconvex lens and resolving at one focal
point. It is an identity mark, not a ray trace, prescription, measurement, or performance
claim.

## Principles

- **Show resolution.** Use one focal point as the memorable finish of the geometry.
- **Keep evidence honest.** Decorative optics never carry values, charts, tolerances, or
  implied measurements.
- **Make precision welcoming.** Curves and terminals are clean and rounded, without a
  clinical or militarized tone.
- **Use optical shorthand carefully.** No rainbow prism, glowing laser, lens flare, or
  pseudo-scientific chart imagery.
- **Stay useful at repository scale.** The icon must survive 32 px display and the header
  must remain legible inside GitHub's content column.

## Palette

| Role | Light | Dark | Use |
| --- | --- | --- | --- |
| Primary ink | `#102A3A` | `#F4F8F7` | Wordmark, rays, primary text |
| Accent teal | `#087F8C` | `#35BEAD` | Lens, focus, non-text emphasis |
| Deep navy | `#102A3A` | `#102A3A` | Icon and README-header field |
| Soft white | `#F4F8F7` | `#F4F8F7` | Light geometry on navy |
| Secondary slate | `#5E7381` | `#B8C9CD` | Supporting copy |

Teal is the only accent. Do not introduce spectral gradients. The translucent fill inside
the header lens uses the same teal and does not create a second accent.

## Geometry

- The square mark uses a `256 x 256` construction field.
- The optical axis is centered at `y = 128`.
- Three rays enter in parallel and share one focal point at `x = 212`.
- The lens is built from two related cubic curves sharing top and bottom terminals.
- Ray strokes are 8 units, lens strokes are 11 units, and all terminals are round.
- The focus uses an accent disc with a small ground-colored center so it remains legible
  when reduced.
- Clear space around the mark is at least the focus-disc diameter.

Do not rotate, skew, add glow, recolor individual rays, or place data labels on the mark.

## Typography

The wordmark uses a clean system sans stack for portable SVG rendering:
`ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`.
Use a semibold weight for the name and ordinary sentence case for supporting copy. Reserve
monospace for commands, file names, units, and measured values.

## Assets

| Asset | Canvas | Background | Intended use |
| --- | ---: | --- | --- |
| `assets/brand/mark.svg` | 256 x 256 | Transparent | Light surfaces |
| `assets/brand/mark-dark.svg` | 256 x 256 | Transparent | Dark surfaces |
| `assets/brand/icon.svg` | 512 x 512 | Deep navy | Source for app and marketplace icon |
| `assets/brand/logo.svg` | 1024 x 256 | Transparent | Light-theme wordmark |
| `assets/brand/logo-dark.svg` | 1024 x 256 | Transparent | Dark-theme wordmark |
| `assets/brand/header.svg` | 1200 x 280 | Deep navy | README header |
| `assets/brand/social-preview.svg` | 1280 x 640 | Deep navy | GitHub social preview source |
| `assets/icon.png` | 512 x 512 | Deep navy | Raster icon export |
| `assets/logo.png` | 1024 x 256 | Transparent | Raster light-theme wordmark |
| `assets/logo-dark.png` | 1024 x 256 | Transparent | Raster dark-theme wordmark |
| `assets/social-preview.png` | 1280 x 640 | Deep navy | GitHub social preview upload |

Recommended README alt text: `optical-design: inspectable tools for practical optical
engineering.`

Recommended icon alt text: `optical-design lens and focus mark.`

## Usage

Use `header.svg` as the README's opening brand image. Use the transparent wordmarks where
the surrounding surface supplies a predictable light or dark ground. Use `icon.png` where
a square raster asset is required. Use `social-preview.png` for the GitHub repository
social preview and retain `social-preview.svg` as its editable source.

Keep the header tagline with the header only. Body documentation should use plain product
language and existing heading styles rather than recreating the brand lockup in text.
