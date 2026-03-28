#!/usr/bin/env python3
"""
Q11 Mapper: Top Referrer Domains
Emits: <referrer_domain> \t 1
"""
import sys, os, re
sys.path.append(os.getcwd())
from log_parser import parse_line

DOMAIN_RE = re.compile(r'https?://([^/]+)')

def extract_domain(referrer):
    if referrer == "-" or not referrer:
        return "direct"
    m = DOMAIN_RE.match(referrer)
    return m.group(1) if m else "other"

for line in sys.stdin:
    entry = parse_line(line)
    if entry:
        domain = extract_domain(entry.referrer)
        print(f"{domain}\t1")
