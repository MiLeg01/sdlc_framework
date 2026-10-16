---
name: accessibility-review
description: Independently review a completed interface or artifact for accessibility through automated checks, keyboard journeys, focus behavior, reflow, contrast, motion, semantics, and assistive-technology evidence, then prioritize and retest findings. Use before consequential UI acceptance or release. Do not use to invent the initial design, replace user research or formal conformance certification, or claim accessibility from visual inspection alone.
---

# Review accessibility

Define the artifact, routes, states, representative viewports, supported input modes, target standard,
and known exclusions before testing. Prefer a fresh reviewer when the implementation is consequential.

## Build the review matrix

Cover each primary journey and state across:

- automated semantic and rule-based scanning;
- keyboard-only traversal, activation, escape, and visible focus;
- focus order, focus restoration, dialogs, errors, and dynamic updates;
- zoom, text spacing, narrow reflow, orientation, and content clipping;
- foreground, non-text, focus-indicator, and state contrast;
- reduced motion, animation control, time limits, and flashing risk;
- names, roles, states, landmarks, headings, labels, instructions, and error association;
- representative screen-reader or accessibility-tree inspection where the environment supports it.

## Execute and record

1. Establish a known working baseline and capture tool, browser, platform, and viewport details.
2. Exercise real journeys instead of scanning only the initial page.
3. Record each finding with a stable ID, affected state, reproduction, expected behavior, observed
   behavior, evidence, impact, standard mapping when known, confidence, and severity.
4. Separate confirmed defects, likely defects needing assistive validation, tooling limitations, and
   advisory improvements. Never convert an unavailable test into a pass.
5. Rank by user impact and journey blockage, not by tool count.

## Retest

Retest the exact reproduction after correction, then run a bounded regression across related states and
input modes. Report PASS, PASS_WITH_LIMITATIONS, or FAIL with unresolved findings and inaccessible test
surfaces. Visual QA and accessibility review may share evidence, but neither substitutes for the other.

Frontend, UX, visual, or accessibility reviewer roles should execute the relevant skills at task time;
do not create permanent wrapper agents whose only behavior is this workflow.
