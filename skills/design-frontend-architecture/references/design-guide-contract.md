# Frontend design-guide contract

Record only fields supported by supplied evidence. Omitted fields remain unknown rather than receiving
defaults that look like accepted decisions.

- product jobs, users, environments, supported devices, and critical journeys;
- visual and interaction source of truth, token source, component library, iconography, and content rules;
- accessibility target, keyboard behavior, reduced motion, localization, zoom, and reflow expectations;
- density, breakpoints, browser support, performance budgets, offline expectations, and packaging limits;
- routing, rendering, authentication, authorization, data freshness, persistence, reset, and telemetry needs;
- existing repository boundaries, dependencies, accepted decisions, protected paths, and migration limits.

For each item, record status as observed, accepted, proposed, assumed, conflicting, or unknown and include a
relocatable source. The architecture may propose missing decisions but must not relabel them as requirements.
