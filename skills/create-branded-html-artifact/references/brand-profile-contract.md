# Evidence-derived brand profile contract

Use this contract when a branded HTML artifact must be regenerated deterministically, especially when a
living dashboard consumes the visual system.

The version-2 JSON profile records:

- a stable generic identifier, display name, whether client branding is required, and resolution status;
- requested and resolved URLs, capture time, HTML, stylesheet, manifest, metadata, non-fatal capture warnings,
  media types, hashes, and source fingerprint;
- exact official favicon and logo/wordmark records, including validated static inline SVG fragments, with
  source URL, source kind, media type, SHA-256, offline target, and unchanged embedded bytes;
- exact observed colors and website usage, concise signals with stable evidence IDs and confidence;
- complete dashboard theme tokens for colors, typography, geometry, and a restrained signature rule;
- an evidence mapping for every theme token with `observed` or `derived` classification, confidence,
  rationale, and source reference, plus explicit observed parents and method for every derived color token;
- deterministic source, asset, theme, and profile fingerprints.

Do not mark required client branding resolved until the supplied source has actually been inspected. A
profile that is unresolved, blocked, stale, incompletely mapped, unsafe for CSS, or identical to a generic
theme must not be consumed as client branding. Record the client profile failure and generate the requested
HTML with the bundled Accenture fallback instead; do not silently label that output as client-branded.

Resolve a supplied official URL deterministically:

```bash
python3 scripts/resolve_brand_profile.py --url <official-url> --id <stable-brand-id> --output brand/profile.json
```

The resolver first accepts a complete official `--brand-*` custom-property set. If that fast path is not
available, it evaluates ordinary CSS selectors and declarations using semantic role evidence, frequency,
visible DOM matches, contrast, and accessibility. Ordinary custom-property references are resolved before
their selector usage is scored, without allowing scoped self-references to erase concrete definitions.
Base interface declarations are distinguished from hover, active, selected, visited, and disabled states so
repeated compiled state rules do not become the global primary by frequency alone. Functional status meaning
is taken from the styled subject, a directly related state selector, or an explicit token rather than an
unrelated ancestor page name. Repetitive generic-link evidence is bounded so it cannot outrank explicit primary
tokens and control fills. Text,
surface, and fill roles retain role-specific contrast rules. It may derive missing roles or minimally adjusted
accessible variants only when the exact observations, source references, method, and confidence remain recorded. Missing
optional status, typography, or geometry evidence uses explicit low-confidence defaults and does not invalidate
a usable identity. Resolution fails closed with a complete actionable diagnostic list when the source is
inaccessible, an explicit identity asset is unsafe or mismatched, or the official logo or core
primary/background/text palette remains unsupported. Do not add client-specific selector names or colors to
this reusable skill.

Official image candidates are downloaded as bounded byte streams, checked against their declared media
types, rejected when SVG content contains active code or external references, hashed, and embedded as data
URIs. Inline SVG candidates are extracted byte-for-byte only when the element or surrounding markup has
identity semantics, then pass the same static-SVG safety checks. Visible CSS image declarations with logo or
wordmark semantics are also candidates; linked files and decoded data URIs retain exact bytes and pass the
same validation. Explicit logo metadata, JSON-LD, linked logo assets, manifest identity icons, and favicons
are ranked below direct inline SVG or image logo evidence.
Social-preview images alone do not qualify as logos. The validator recomputes the hashes, checks byte
signatures against declared media types, rejects unsafe SVG content, and enforces contrast for theme tokens
that downstream artifacts render as text or focus indicators.

The resolver must follow redirects and inspect linked source evidence. It requests identity transfer encoding
and also decodes bounded gzip and deflate responses because ordinary servers may ignore that preference.
Unsupported or invalid encodings and decompression over the capture limit fail closed. When the official website is
inaccessible or the logo/wordmark or core semantic palette cannot be resolved, it returns a blocked
client-brand result. An absent favicon may reuse the exact validated official logo bytes with explicit
provenance; an invalid declared favicon remains a fail-closed error. Both
dashboard and presentation then use the same Accenture fallback identity and still emit their `.html` files;
neither may invent a client profile or claim client-brand fidelity.

For a living dashboard, pass the profile to the generator and validator:

```bash
python3 scripts/build_dashboard.py --data dashboard/data.json --brand-profile brand/profile.json --output dashboard/index.html
python3 scripts/build_dashboard.py --data dashboard/data.json --brand-profile brand/profile.json --output dashboard/index.html --check
python3 scripts/render_branded_html.py --template assets/editorial-shell.html --brand-profile brand/profile.json --output presentation/index.html
python3 scripts/validate_html.py dashboard/index.html --brand-profile brand/profile.json --brand-qa dashboard/brand-qa.json --peer-html presentation/index.html --json
```

The `brand-qa.json` manifest carries per-viewport evidence under `responsive`: desktop, tablet, and mobile
states with computed styles, visible identity, console errors, and horizontal-reflow measurements. Validation
fails when no captured viewport is 480px or narrower, when a state overflows horizontally, or when the
official identity stops being visible at a narrower width.

Keep source excerpts, copied website CSS, proprietary fonts, and screenshots out of the profile. Exact
permitted official favicon/logo bytes are the deliberate exception because the artifacts must work offline
and prove asset identity.
