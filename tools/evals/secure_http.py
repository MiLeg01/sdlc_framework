#!/usr/bin/env python3
"""Small HTTPS helpers that prevent credentials crossing redirect origins."""

from __future__ import annotations

import urllib.request
from urllib.parse import urlsplit


SENSITIVE_HEADERS = (
    "Authorization",
    "api-key",
    "Proxy-Authorization",
    "Ocp-Apim-Subscription-Key",
    "x-client-userkey",
    "x-client-username",
)


def https_origin(url: str, *, label: str = "URL") -> tuple[str, str, int]:
    parsed = urlsplit(url)
    if parsed.scheme.lower() != "https":
        raise ValueError(f"{label} must use HTTPS")
    if not parsed.hostname or parsed.username is not None or parsed.password is not None:
        raise ValueError(f"{label} must have a host and no user information")
    try:
        port = parsed.port or 443
    except ValueError as exc:
        raise ValueError(f"{label} has an invalid port") from exc
    if port != 443:
        raise ValueError(f"{label} must use the default HTTPS port")
    return ("https", parsed.hostname.casefold(), port)


def azure_devops_origin(url: str, *, label: str = "Azure collection URI") -> tuple[str, str, int]:
    origin = https_origin(url, label=label)
    hostname = origin[1]
    if hostname != "dev.azure.com" and not hostname.endswith(".visualstudio.com"):
        raise ValueError(f"{label} must use dev.azure.com or an Azure DevOps visualstudio.com host")
    return origin


class CredentialSafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Preserve ordinary redirects but strip credentials when the origin changes."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None and https_origin(req.full_url) != https_origin(newurl):
            for header in SENSITIVE_HEADERS:
                redirected.remove_header(header)
        return redirected


def secure_urlopen(request: urllib.request.Request, timeout: int):
    https_origin(request.full_url)
    opener = urllib.request.build_opener(CredentialSafeRedirectHandler())
    return opener.open(request, timeout=timeout)


def credentialed_download(
    url: str,
    token: str,
    *,
    credential_origin: str,
    timeout: int,
    max_bytes: int,
) -> bytes:
    target_origin = https_origin(url, label="download URL")
    trusted_origin = https_origin(credential_origin, label="credential origin")
    headers = {"Authorization": f"Bearer {token}"} if target_origin == trusted_origin else {}
    request = urllib.request.Request(url, headers=headers)
    with secure_urlopen(request, timeout=timeout) as response:
        payload = response.read(max_bytes + 1)
    if len(payload) > max_bytes:
        raise ValueError(f"download exceeds {max_bytes} bytes")
    return payload
