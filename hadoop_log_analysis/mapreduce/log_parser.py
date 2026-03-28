#!/usr/bin/env python3
"""
log_parser.py – Shared Apache/Nginx Combined Log Format parser.
Import this in any mapper/reducer, or run standalone to test parsing.

Format:
  IP - - [DD/Mon/YYYY:HH:MM:SS +ZONE] "METHOD URL PROTO" STATUS BYTES "REF" "UA" RESPONSE_MS
"""

import re
from dataclasses import dataclass
from typing import Optional

# Combined Log Format + optional response-time field
LOG_PATTERN = re.compile(
    r'(?P<ip>\S+)'           # client IP
    r'\s+\S+\s+\S+'          # ident, auth (usually "- -")
    r'\s+\[(?P<datetime>[^\]]+)\]'  # [DD/Mon/YYYY:HH:MM:SS ±ZONE]
    r'\s+"(?P<method>\S+)'   # HTTP method
    r'\s+(?P<url>\S+)'       # requested URL
    r'\s+(?P<protocol>[^"]+)"'  # HTTP version
    r'\s+(?P<status>\d{3})'  # status code
    r'\s+(?P<bytes>\S+)'     # bytes sent ("-" = 0)
    r'(?:\s+"(?P<referrer>[^"]*)"'  # referrer (optional)
    r'\s+"(?P<user_agent>[^"]*)")?'  # user-agent (optional)
    r'(?:\s+(?P<response_time>\d+))?'  # response time ms (optional)
)

MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


@dataclass
class LogEntry:
    ip: str
    datetime_str: str
    method: str
    url: str
    protocol: str
    status: int
    bytes_sent: int
    referrer: str
    user_agent: str
    response_time_ms: int

    # Derived fields
    @property
    def date(self) -> str:
        """Return YYYY-MM-DD"""
        try:
            d, rest = self.datetime_str.split(":", 1)
            day, mon, year = d.split("/")
            return f"{year}-{MONTHS.get(mon, 0):02d}-{int(day):02d}"
        except Exception:
            return "unknown"

    @property
    def hour(self) -> str:
        """Return YYYY-MM-DD HH"""
        try:
            d, rest = self.datetime_str.split(":", 1)
            day, mon, year = d.split("/")
            hh = rest.split(":")[0]
            return f"{year}-{MONTHS.get(mon, 0):02d}-{int(day):02d} {hh}"
        except Exception:
            return "unknown"

    @property
    def url_path(self) -> str:
        """Strip query string from URL"""
        return self.url.split("?")[0]

    @property
    def is_error(self) -> bool:
        return self.status >= 400

    @property
    def is_bot(self) -> bool:
        ua_lower = self.user_agent.lower()
        return any(b in ua_lower for b in ["bot", "crawler", "spider", "scraper", "curl", "python"])

    @property
    def browser_family(self) -> str:
        ua = self.user_agent
        if "Firefox" in ua:
            return "Firefox"
        if "Chrome" in ua and "Chromium" not in ua:
            return "Chrome"
        if "Safari" in ua and "Chrome" not in ua:
            return "Safari"
        if "MSIE" in ua or "Trident" in ua:
            return "IE"
        if "bot" in ua.lower() or "crawler" in ua.lower():
            return "Bot"
        return "Other"

    @property
    def device_type(self) -> str:
        ua = self.user_agent
        if "Mobile" in ua or "Android" in ua or "iPhone" in ua:
            return "Mobile"
        if "Tablet" in ua or "iPad" in ua:
            return "Tablet"
        return "Desktop"

    @property
    def status_class(self) -> str:
        return f"{self.status // 100}xx"


def parse_line(line: str) -> Optional[LogEntry]:
    """Parse a single log line. Returns None on failure."""
    m = LOG_PATTERN.match(line.strip())
    if not m:
        return None
    g = m.groupdict()
    try:
        return LogEntry(
            ip=g["ip"],
            datetime_str=g["datetime"],
            method=g["method"].upper(),
            url=g["url"],
            protocol=g.get("protocol", "HTTP/1.1").strip(),
            status=int(g["status"]),
            bytes_sent=int(g["bytes"]) if g["bytes"] != "-" else 0,
            referrer=g.get("referrer") or "-",
            user_agent=g.get("user_agent") or "-",
            response_time_ms=int(g["response_time"]) if g.get("response_time") else 0,
        )
    except (ValueError, TypeError):
        return None


if __name__ == "__main__":
    import sys
    for line in sys.stdin:
        entry = parse_line(line)
        if entry:
            print(f"IP={entry.ip} date={entry.date} method={entry.method} "
                  f"url={entry.url_path} status={entry.status} bytes={entry.bytes_sent} "
                  f"browser={entry.browser_family} device={entry.device_type}")
        else:
            print(f"PARSE_FAIL: {line.strip()[:80]}", file=sys.stderr)
