"""
Milestone 6.2: read a personal website the user added, once, when they press
Read it: the saved page plus up to MAX_EXTRA_PAGES pages it links to on the
same site (e.g. /about, /projects). Nothing beyond those, and nothing on
another site.
"""

from __future__ import annotations

import ipaddress
import socket
import urllib.request
from urllib.parse import urldefrag, urljoin, urlparse

MAX_BYTES = 2 * 1024 * 1024
MIN_TEXT_CHARS = 200
MAX_EXTRA_PAGES = 5
_SKIP_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".zip", ".mp4", ".mov", ".css", ".js", ".xml", ".ico")
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


def same_site_links(html: str, page_url: str) -> list[str]:
    """Pages on the same host that this page links to, in page order, without repeats."""
    from bs4 import BeautifulSoup

    base_host = (urlparse(page_url).hostname or "").lower()
    seen = {urldefrag(page_url)[0].rstrip("/")}
    out: list[str] = []
    for a in BeautifulSoup(html, "html.parser").find_all("a", href=True):
        url = urldefrag(urljoin(page_url, a["href"]))[0]
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or (parsed.hostname or "").lower() != base_host:
            continue
        if parsed.path.lower().endswith(_SKIP_EXTENSIONS):
            continue
        key = url.rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        out.append(url)
    return out


def read_site(url: str, *, fetch=None) -> tuple[str, list[str]]:
    """
    Text of the saved page and up to MAX_EXTRA_PAGES same-site pages it links
    to. Returns (combined_text, urls_read). `fetch` returns (text, html) and is
    injectable for tests.
    """
    fetch = fetch or _fetch
    text, html = fetch(url)
    parts = [(url, text)]
    for link in same_site_links(html, url)[:MAX_EXTRA_PAGES]:
        try:
            link_text, _ = fetch(link)
        except WebsiteReadError:
            continue  # a broken link shouldn't spoil the rest
        if link_text.strip():
            parts.append((link, link_text))

    combined = "\n\n".join(f"[Page: {u}]\n{t}" for u, t in parts if t.strip())
    if sum(len(t) for _, t in parts) < MIN_TEXT_CHARS:
        raise WebsiteReadError(
            "Your site has almost no readable text, even on the pages it links to (it may need "
            "JavaScript to load). Upload a PDF of it below instead: in your browser, choose Print → Save as PDF."
        )
    return combined, [u for u, t in parts if t.strip()]


def fetch_page_text(url: str) -> str:
    """Text of a single page (kept for callers that want just one)."""
    return _fetch(url)[0]


def _fetch(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise WebsiteReadError("Only web addresses (http or https) can be read.")
    if not _is_public_host(parsed.hostname):
        raise WebsiteReadError("Addresses on this computer or a local network can't be read.")

    opener = urllib.request.build_opener(_NoRedirectToPrivate)
    req = urllib.request.Request(url, headers={"User-Agent": "letsApplI/profile-reader (on request)"})
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
    if "html" in ctype:
        return html_to_text(raw), raw
    return raw, ""
