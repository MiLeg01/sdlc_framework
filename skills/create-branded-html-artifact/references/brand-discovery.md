# Brand discovery

## Sources

Prefer supplied design systems and assets, then official guidelines, then the client website and approved
reference artifacts, then manually described direction. Record source URL/path, capture date/version,
observed signal, confidence, license/usage constraint, and whether it is factual or visual-only.

For a supplied official URL, follow redirects and capture the resolved HTML, linked stylesheets, web
manifest, metadata and structured data, favicon/icon variants, linked logo assets, image candidates, and
inline SVG logo/wordmark candidates. Request identity transfer encoding, but safely decode bounded gzip and
deflate responses when the server still compresses the evidence. Preserve the requested and final
URLs, media types, and SHA-256 hashes. If the source or required identity cannot be inspected reliably,
record client branding as blocked or unresolved, then generate the requested HTML with the bundled Accenture
fallback. Preserve the failed source and reason; never present the fallback as client-derived branding.

When the source identifies the client organization, geography, or public mandate, record those observations
separately from visual signals so the initializer can resolve client sector and locale. A government-style
domain is evidence, not conclusive classification by itself; explicit private-sector or contradictory
organization evidence wins. Brand analysis and sector/locale resolution may proceed concurrently.

## Extract

- exact primary, secondary, functional, surface, text, link, focus, and semantic colors plus their observed usage;
- display, body, and data typography roles plus licensed fallbacks;
- spacing rhythm, grid, density, borders, radius, shadow, and icon language;
- imagery/diagram conventions and logo clear-space/placement rules;
- motion, interaction, voice, and accessibility constraints.

Use complete `--brand-*` custom properties first when the official source exposes them. Otherwise inspect
ordinary and compiled CSS declarations. Retain the selector, property, source URL, frequency, and semantic
context for each exact color rather than treating a palette scrape as sufficient evidence. Resolve arbitrary
custom-property references through their concrete definitions,
while disregarding scoped self-references that do not redefine the root value. Keep page backgrounds, card
surfaces, text foregrounds, and control fills distinct when ranking colors. Apply contrast to the role in which
the color will render: text colors against their surface, focus indicators against adjacent surfaces, and an
accessible foreground against primary/header fills. Record whether a selector matches elements present in the
captured HTML. Prefer repeated visible interface use in primary
buttons, active navigation, headings, links, focus outlines, validation errors, success messages, page
backgrounds, cards, text, and borders. Check foreground/background contrast before accepting text, focus,
header, or on-dark roles. Treat hover, active, selected, visited, and disabled declarations as state evidence;
they can reinforce a palette but must not outrank a repeatedly observed base primary solely because compiled
CSS repeats state rules. Likewise, attach danger or success semantics to the styled subject, a directly related
state selector, or an explicit functional token. An error-page ancestor does not make every button or label
inside it a danger-colored control, and substrings such as `complete` inside an unrelated identifier do not
establish success. Bound frequency contributions from generic links so repeated framework utilities do not
outweigh explicit primary tokens and control backgrounds. Honor linked-stylesheet and declaration order when the
custom-property fast path is used. A failed optional stylesheet or manifest is a recorded capture warning,
not a reason to discard otherwise complete evidence.

Rank interface evidence independently from identity artwork. Colors observed only in a logo, wordmark, or
social icon are identity evidence, not global UI colors. Error and danger selectors establish a functional
danger role and must not promote that color to primary, header, or signature use. When a required role has
no defensible candidate, report all missing roles together and use the fallback.

Open Graph and social-preview images are metadata evidence, not logo candidates. Require logo or wordmark
semantics in inline SVG, image markup, explicit logo metadata or JSON-LD, a linked logo asset, or another
official identity source. Also inspect visible logo-semantic CSS `background-image`, `mask`, and `content`
declarations, including static image data URIs. Decode and preserve their exact bytes, and apply the same
media-type, hash, size, and static-SVG safety checks used for linked assets. Manifest icons and favicons are
lower-confidence identity candidates and are used
as the logo only when no stronger candidate exists. If an explicit logo candidate is unsafe, inaccessible,
or mismatched, fail closed rather than hiding the problem behind a weaker icon. If no favicon is declared,
the exact validated official logo bytes may be reused as the offline icon with a recorded warning.

If an observed optional semantic text color is inaccessible, first prefer an exact accessible official
color with the same semantic or hue evidence. Otherwise derive the smallest deterministic lightness change
needed for contrast and retain the exact original color in observed evidence. If optional success or danger
roles are absent, use clearly identified low-confidence accessible functional defaults; do not promote those
defaults as client colors. Missing safe font, radius, or border declarations may likewise use restrained
low-confidence local defaults. These optional gaps must not discard a usable logo and evidenced primary,
background, and text palette.

Typography may be inferred from repeated `font-family` declarations, with heading/display selectors taking
precedence for the display role and safe local fallbacks appended. Ignore icon fonts and unlicensed custom
faces. Select restrained radii and border widths from ordinary declarations. A signature rule may reuse an
observed secondary interface color and observed border thickness; record this as an interpreted decision.

## Translate, do not clone

Build a purpose-specific system that preserves recognition without copying the marketing-site layout.
Download or embed the selected official favicon and permitted logo unchanged. Dashboard and presentation
must use the same bytes and hashes without hot-linking. Do not redraw official marks, synthesize favicons,
infer proprietary fonts, invent brand claims, or import tracking/runtime dependencies. Derived colors are
allowed only for a missing role or to make an evidenced role safe for its rendered use, and only with explicit
provenance, deterministic method, and confidence. Preserve exact static inline SVG bytes, but reject scripts,
event handlers, foreign objects, document/entity declarations, non-embedded external references, unsupported
media, empty files, or bytes that do not match the declared media type.

Use website evidence as identity input only. Do not copy its page layout, navigation, content, or component
composition into the generated dashboard or presentation.

## Anti-template review

Reject choices that could be swapped into any client without changing meaning: neon AI palettes, purple
gradients, glass cards, unexplained metric tiles, decorative network diagrams, excessive rounded cards,
or a generic editorial theme unrelated to the subject. Spend distinctiveness on one defensible signature
derived from the client's domain; keep the rest disciplined.
