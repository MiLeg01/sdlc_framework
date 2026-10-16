#!/usr/bin/env python3
"""Render the canonical presentation shell with one resolved brand profile."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


BRAND_SCRIPTS = Path(__file__).resolve().parents[2] / "build-living-dashboard" / "scripts"
sys.path.insert(0, str(BRAND_SCRIPTS))
from brand_profile import (  # noqa: E402
    accenture_fallback_attributes,
    accenture_fallback_css,
    accenture_fallback_favicon,
    accenture_fallback_logo,
    brand_attributes,
    favicon_markup,
    logo_markup,
    render_brand_css,
    validate_brand_profile,
)


PLACEHOLDERS = {
    "__BRAND_ATTRIBUTES__", "__BRAND_FAVICON__", "__BRAND_STYLE__", "__BRAND_LOGO__", "__BRAND_PROFILE_JSON__",
}


def render(template: str, profile: dict[str, object]) -> str:
    missing = sorted(placeholder for placeholder in PLACEHOLDERS if placeholder not in template)
    if missing:
        raise ValueError(f"branded HTML template is missing placeholders: {missing}")
    payload = json.dumps(profile, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (template
            .replace("__BRAND_ATTRIBUTES__", brand_attributes(profile))
            .replace("__BRAND_FAVICON__", favicon_markup(profile))
            .replace("__BRAND_STYLE__", render_brand_css(profile))
            .replace("__BRAND_LOGO__", logo_markup(profile, "artifact-brand-logo"))
            .replace("__BRAND_PROFILE_JSON__", payload))


def render_accenture_fallback(template: str, requested_source: str | None, reason: str) -> str:
    missing = sorted(placeholder for placeholder in PLACEHOLDERS if placeholder not in template)
    if missing:
        raise ValueError(f"branded HTML template is missing placeholders: {missing}")
    payload = json.dumps({
        "id": "accenture-fallback",
        "status": "fallback",
        "requested_brand_source": requested_source,
        "client_brand_resolved": False,
        "fallback_reason": reason,
    }, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (template
            .replace("__BRAND_ATTRIBUTES__", accenture_fallback_attributes())
            .replace("__BRAND_FAVICON__", accenture_fallback_favicon())
            .replace("__BRAND_STYLE__", accenture_fallback_css())
            .replace("__BRAND_LOGO__", accenture_fallback_logo("artifact-brand-logo"))
            .replace("__BRAND_PROFILE_JSON__", payload))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--brand-profile", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        template = args.template.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"BRANDED HTML BLOCKED: {exc}", file=sys.stderr)
        return 1
    if args.brand_profile:
        try:
            profile = validate_brand_profile(json.loads(args.brand_profile.read_text(encoding="utf-8")))
            expected = render(template, profile)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            expected = render_accenture_fallback(template, str(args.brand_profile), str(exc))
            print(f"client branding unavailable; using Accenture fallback: {exc}", file=sys.stderr)
    else:
        expected = render_accenture_fallback(template, None, "no brand profile supplied")
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != expected:
            print(f"branded HTML drift: {args.output}")
            return 1
        print(f"branded HTML current: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(expected, encoding="utf-8")
    temporary.replace(args.output)
    print(f"generated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
