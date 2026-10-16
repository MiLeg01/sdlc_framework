---
name: frontend-design
description: Establish and implement a distinctive, intentional product-interface direction covering hierarchy, typography, responsive composition, component language, data density, and interaction states. Use for new application UI or material redesign where visual and product decisions are part of the work. Do not use for one-off narrative presentations, brand-only styling, small maintenance edits, or downstream validation of an already complete interface.
---

# Design a frontend product interface

Start from the product job, users, environment, content, workflows, constraints, existing design system,
and implementation stack. Preserve established conventions unless the task explicitly authorizes a redesign.

## Choose a visual thesis

1. State the experience in concrete terms: operational, editorial, technical, calm, dense, playful, or
   another defensible direction grounded in the product.
2. Define hierarchy, typography, spacing rhythm, color roles, surfaces, borders, iconography, imagery,
   and motion as one coherent system.
   Express repeated decisions through a compact token layer for type roles, content measures, section and
   component spacing, border hierarchy, surfaces, radii, shadow, and transition timing.
3. Avoid generic card grids, decorative gradients, excessive pills, stock dashboard chrome, and arbitrary
   glass effects unless evidence supports them.
4. Reuse a supplied design system or verified brand source before introducing new primitives.

## Compose the product

Map navigation, primary work, secondary context, empty/loading/error/success/disabled states, dense data,
forms, destructive actions, and responsive transformations. Make the most important action and information
visually obvious without flattening everything into equal emphasis.

## Implement deliberately

1. Build reusable semantic components with explicit variants and state behavior.
2. Keep responsiveness content-driven; test narrow, wide, zoomed, and touch contexts.
3. Treat keyboard focus, contrast, reduced motion, readable type, and target size as design inputs, then
   hand the completed artifact to `accessibility-review` for independent evidence.
4. Use motion sparingly to communicate relationship, causality, or state.
5. Inspect the real rendered interface throughout implementation, not only at the end.
   When the structure and behavior are correct but the result is not yet finished, use the bounded
   `polish-html-artifact` workflow before independent validation.

## Handoff

Record the visual thesis, source constraints, component and token decisions, responsive rules, interaction
states, intentional exceptions, and validation matrix. Delegate a fresh frontend or visual review at task
time when independence matters; do not promote a wrapper role that merely repeats this skill.
