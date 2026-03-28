#!/usr/bin/env python3
"""
Q13 Mapper: Suspicious IP Detection
Flags IPs with many 4xx errors or hitting sensitive paths.
Emits: <ip> \t error|1   or   <ip> \t sensitive|1
"""
import sys, os
sys.path.append(os.getcwd())
from log_parser import parse_line

SENSITIVE_PATHS = {
    "/admin", "/wp-login.php", "/xmlrpc.php", "/.env",
    "/config", "/backup", "/.git", "/phpmyadmin",
    "/wp-admin", "/shell", "/cmd",
}

for line in sys.stdin:
    entry = parse_line(line)
    if entry:
        if entry.status in (401, 403, 404, 429):
            print(f"{entry.ip}\terror|1")
        if any(entry.url_path.startswith(p) for p in SENSITIVE_PATHS):
            print(f"{entry.ip}\tsensitive|1")
        if entry.is_bot:
            print(f"{entry.ip}\tbot|1")
