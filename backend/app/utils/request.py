from ipaddress import ip_address

from fastapi import Request
from user_agents import parse


LOCAL_IPS = {"127.0.0.1", "0.0.0.0", "::1", "localhost"}
BROWSER_FALLBACKS = [
    ("Edge", "Edg"),
    ("Chrome", "Chrome"),
    ("Firefox", "Firefox"),
    ("Safari", "Safari"),
]
OS_FALLBACKS = [
    ("Windows", "Windows"),
    ("macOS", "Mac OS X"),
    ("iOS", "iPhone"),
    ("iOS", "iPad"),
    ("Android", "Android"),
    ("Linux", "Linux"),
]


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "").strip()
    if forwarded_for:
        first_ip = forwarded_for.split(",", 1)[0].strip()
        if first_ip:
            return first_ip

    real_ip = request.headers.get("x-real-ip", "").strip()
    if real_ip:
        return real_ip

    return request.client.host if request.client else ""


def parse_device(user_agent: str) -> str:
    if not user_agent:
        return "未知/未知"

    ua = parse(user_agent)
    browser = ua.browser.family or _fallback_match(user_agent, BROWSER_FALLBACKS) or "未知浏览器"
    os_name = ua.os.family or _fallback_match(user_agent, OS_FALLBACKS) or "未知系统"
    return f"{browser}/{os_name}"


def describe_ip_location(ip: str) -> str:
    if not ip:
        return "未知"
    if ip in LOCAL_IPS:
        return "本机"

    try:
        parsed_ip = ip_address(ip)
    except ValueError:
        return "未知"

    if parsed_ip.is_loopback or parsed_ip.is_unspecified:
        return "本机"
    if parsed_ip.is_private:
        return "内网"
    return "未知"


def _fallback_match(user_agent: str, patterns: list[tuple[str, str]]) -> str | None:
    for name, marker in patterns:
        if marker in user_agent:
            return name
    return None
