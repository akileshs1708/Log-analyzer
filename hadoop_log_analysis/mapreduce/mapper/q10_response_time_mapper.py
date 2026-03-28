#!/usr/bin/env python3
"""
Q10 Mapper: Average Response Time per URL
Emits: <url_path> \t <response_time_ms>|1
"""
import sys, os
sys.path.append(os.getcwd())
from log_parser import parse_line

for line in sys.stdin:
    entry = parse_line(line)
    if entry and entry.response_time_ms > 0:
        print(f"{entry.url_path}\t{entry.response_time_ms}|1")
