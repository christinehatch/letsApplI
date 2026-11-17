"""
Milestone 6.2: read the text of one web page the user added, once, when they
press Read it. No crawling: only the exact URL they saved.
"""

from __future__ import annotations

import ipaddress
import socket
import urllib.request
from urllib.parse import urlparse

MAX_BYTES = 2 * 1024 * 1024
MIN_TEXT_CHARS = 200
TIMEOUT_S = 15


class WebsiteReadError(Exception):
    """The page couldn't be read; the message is safe to show the user."""


def _is_public_host(host: str) -> bool:
    """Refuse addresses on this machine or the local network."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        raise WebsiteReadError("That website address couldn't be found. Check it and try again.")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    return True


class _NoRedirectToPrivate(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        host = urlparse(newurl).hostname or ""
        if urlparse(newurl).scheme not in ("http", "https") or not _is_public_host(host):
            raise WebsiteReadError("That page redirects somewhere that can't be read.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def html_to_text(html: str) -> str:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "template", "iframe"]):
        tag.decompose()
    lines = [" ".join(line.split()) for line in soup.get_text("\n").splitlines()]
    return "\n".join(line for line in lines if line)


def fetch_page_text(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise WebsiteReadError("Only web addresses (http or https) can be read.")
    if not _is_public_host(parsed.hostname):
        raise WebsiteReadError("Addresses on this computer or a local network can't be read.")

    opener = urllib.request.build_opener(_NoRedirectToPrivate)
    req = urllib.request.Request(url, headers={"User-Agent": "letsApplI/profile-reader (one page, on request)"})
    try:
        with opener.open(req, timeout=TIMEOUT_S) as resp:
            ctype = (resp.headers.get("Content-Type") or "").lower()
            if "html" not in ctype and "text/plain" not in ctype:
                raise WebsiteReadError("That address isn't a web page. Upload the file instead.")
            body = resp.read(MAX_BYTES + 1)
            charset = resp.headers.get_content_charset() or "utf-8"
    except WebsiteReadError:
        raise
    except Exception:
        raise WebsiteReadError("Couldn't load that page. Check the address, or try again later.")

    if len(body) > MAX_BYTES:
        body = body[:MAX_BYTES]
    raw = body.decode(charset, errors="replace")
    text = html_to_text(raw) if "html" in ctype else raw
    if len(text) < MIN_TEXT_CHARS:
        raise WebsiteReadError(
            "That page has almost no readable text (it may need JavaScript to load). "
            "Save it as a PDF from your browser and upload that instead."
        )
    return text
