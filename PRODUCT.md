# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

People with varied optics experience who need an inspectable assistant workflow for
calculation, saved-model work, validation, and review. The repository is a working tool,
not a course: public documentation explains its use without assuming prior familiarity.

## Product Purpose

`optical-design` gives supported AI coding agents one shared, versioned optical-design
skill. It helps users calculate optical performance, work on sequential lens models, and
turn results into reviewable evidence without hiding inputs, edits, or failed checks.

## Positioning

The repository packages one inspectable skill across multiple agents and keeps numerical
results, model changes, acceptance criteria, provenance, and review artifacts visible to
the user.

## Operating Context

Users install the skill into an agent project, then run its Python tools through `uv`.
Portable work uses Optiland. Native OpticStudio work requires Windows and an appropriate
API license. Typical work includes calculation, model inspection, controlled edits,
refocus and optimization, sensitivity and tolerance analysis, validation, and review
package generation.

## Capabilities and Constraints

- Node.js 22 or newer is required for the distribution CLI.
- Python 3.11 or newer and `uv` are required to run the optical tools.
- The installer is dependency-free JavaScript and does not use install lifecycle scripts.
- Managed installation operations preserve ownership and refuse unsafe paths, symlinks,
  unmanaged replacements, and edited installations.
- Release 1.1.0 expands distribution and onboarding without changing the released optical
  algorithms.
- A logo or diagram is identity material only. It must never imply measured performance,
  native execution, or optical acceptance.

## Brand Commitments

- Name: `optical-design`.
- Voice: precise, calm, welcoming, and candid about evidence limits.
- Audience balance: readable to people new to optics while retaining precise terminology.
- Identity: original lens and focus geometry, restrained teal, high-contrast neutral navy,
  and no prism-rainbow shorthand.
- Light and dark presentation must remain legible at repository-header and icon sizes.

## Evidence on Hand

The repository includes public documentation, portable examples, tests, recorded research,
and release-evidence artifacts. These sources may support claims only within their stated
scope. The visual identity carries no performance claim.

## Product Principles

1. Make the first useful workflow easy to start.
2. Keep inputs, assumptions, mutations, failures, and saved artifacts inspectable.
3. Distinguish portable results from licensed native execution.
4. Preserve user files and require explicit scope for destructive or global operations.
5. Use the same bundled skill as the source of truth across supported agents.

## Accessibility & Inclusion

Repository branding and onboarding must remain readable in light and dark GitHub themes,
at small icon sizes, and for readers with varied optical-design experience.
