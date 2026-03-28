#!/usr/bin/env python3
"""
run_all_jobs.py
---------------
Master orchestrator for all 13 MapReduce log analysis jobs.

Modes:
  --local   : Run locally using Unix pipes (no Hadoop needed, great for testing)
  --hadoop  : Submit to Hadoop via Streaming (requires HADOOP_HOME set)

Usage:
  python run_all_jobs.py --local  --input data/access.log --output results/
  python run_all_jobs.py --hadoop --input hdfs:///logs/access.log --output hdfs:///results/
"""

import argparse
import subprocess
import os
import sys
import time
from pathlib import Path

# ── Job definitions ────────────────────────────────────────────────────────────
JOBS = [
    {
        "id": "q01", "name": "Requests per IP Address",
        "mapper":  "mapreduce/mapper/q01_ip_requests_mapper.py",
        "reducer": "mapreduce/reducer/q01_ip_requests_reducer.py",
        "output":  "q01_ip_requests",
    },
    {
        "id": "q02", "name": "Most Requested URLs",
        "mapper":  "mapreduce/mapper/q02_url_requests_mapper.py",
        "reducer": "mapreduce/reducer/q02_url_requests_reducer.py",
        "output":  "q02_url_requests",
    },
    {
        "id": "q03", "name": "Requests per Day & Hour",
        "mapper":  "mapreduce/mapper/q03_time_requests_mapper.py",
        "reducer": "mapreduce/reducer/q03_time_requests_reducer.py",
        "output":  "q03_time_requests",
    },
    {
        "id": "q04", "name": "HTTP Status Code Distribution",
        "mapper":  "mapreduce/mapper/q04_status_codes_mapper.py",
        "reducer": "mapreduce/reducer/q04_status_codes_reducer.py",
        "output":  "q04_status_codes",
    },
    {
        "id": "q05", "name": "Bandwidth Consumed per URL",
        "mapper":  "mapreduce/mapper/q05_bandwidth_mapper.py",
        "reducer": "mapreduce/reducer/q05_bandwidth_reducer.py",
        "output":  "q05_bandwidth",
    },
    {
        "id": "q06", "name": "Top Error URLs (4xx/5xx)",
        "mapper":  "mapreduce/mapper/q06_error_urls_mapper.py",
        "reducer": "mapreduce/reducer/q06_error_urls_reducer.py",
        "output":  "q06_error_urls",
    },
    {
        "id": "q07", "name": "HTTP Method Distribution",
        "mapper":  "mapreduce/mapper/q07_http_methods_mapper.py",
        "reducer": "mapreduce/reducer/q07_http_methods_reducer.py",
        "output":  "q07_http_methods",
    },
    {
        "id": "q08", "name": "Browser Family Distribution",
        "mapper":  "mapreduce/mapper/q08_browser_mapper.py",
        "reducer": "mapreduce/reducer/q08_browser_reducer.py",
        "output":  "q08_browsers",
    },
    {
        "id": "q09", "name": "Device Type Distribution",
        "mapper":  "mapreduce/mapper/q09_device_mapper.py",
        "reducer": "mapreduce/reducer/q09_device_reducer.py",
        "output":  "q09_devices",
    },
    {
        "id": "q10", "name": "Avg Response Time per URL",
        "mapper":  "mapreduce/mapper/q10_response_time_mapper.py",
        "reducer": "mapreduce/reducer/q10_response_time_reducer.py",
        "output":  "q10_response_time",
    },
    {
        "id": "q11", "name": "Top Referrer Domains",
        "mapper":  "mapreduce/mapper/q11_referrer_mapper.py",
        "reducer": "mapreduce/reducer/q11_referrer_reducer.py",
        "output":  "q11_referrers",
    },
    {
        "id": "q12", "name": "Hourly Traffic Pattern (0-23)",
        "mapper":  "mapreduce/mapper/q12_hourly_pattern_mapper.py",
        "reducer": "mapreduce/reducer/q12_hourly_pattern_reducer.py",
        "output":  "q12_hourly_pattern",
    },
    {
        "id": "q13", "name": "Suspicious IP Detection",
        "mapper":  "mapreduce/mapper/q13_suspicious_ip_mapper.py",
        "reducer": "mapreduce/reducer/q13_suspicious_ip_reducer.py",
        "output":  "q13_suspicious_ips",
    },
]


# ── Local runner (pipe: cat | sort | mapper | sort | reducer) ──────────────────
def run_local(job, input_file, output_dir):
    out_file = os.path.join(output_dir, job["output"] + ".tsv")
    env = f"PYTHONPATH=/home/claude/hadoop_log_analysis"
    cmd = (
        f"{env} python3 {job['mapper']} < '{input_file}' "
        f"| sort "
        f"| {env} python3 {job['reducer']} "
        f"> '{out_file}'"
    )
    t0 = time.time()
    ret = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    elapsed = time.time() - t0
    if ret.returncode != 0:
        print(f"  ✗ STDERR: {ret.stderr[:300]}")
        return False, elapsed
    lines = sum(1 for _ in open(out_file))
    print(f"  ✓ {out_file}  ({lines} output rows, {elapsed:.1f}s)")
    return True, elapsed


# ── Hadoop Streaming runner ────────────────────────────────────────────────────
def run_hadoop(job, input_path, output_base, hadoop_streaming_jar):
    output_path = output_base.rstrip("/") + "/" + job["output"]
    subprocess.run(
    ["hadoop", "fs", "-rm", "-r", "-f", output_path],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
    )

    mapper_file = os.path.basename(job["mapper"])
    reducer_file = os.path.basename(job["reducer"])

    cmd = [
        "hadoop", "jar", hadoop_streaming_jar,
        "-files", ",".join([
        f"/app/{job['mapper']}",
        f"/app/{job['reducer']}",
        "/app/mapreduce/log_parser.py"
            ]),   
        "-input",   input_path,
        "-output",  output_path,
        "-mapper", f"/usr/bin/python3 {mapper_file}",
        "-reducer", f"/usr/bin/python3 {reducer_file}",
         
        ]
    t0 = time.time()
    ret = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0
    if ret.returncode != 0:
        print("\nJOB FAILED")
        print("CMD:", " ".join(cmd))
        print("STDOUT:\n", ret.stdout)
        print("STDERR:\n", ret.stderr)
        return False, elapsed
    print(f"  ✓ {output_path}  ({elapsed:.1f}s)")
    return True, elapsed


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Hadoop Log Analysis – Job Runner")
    parser.add_argument("--local",   action="store_true", help="Run locally (no Hadoop)")
    parser.add_argument("--hadoop",  action="store_true", help="Run on Hadoop cluster")
    parser.add_argument("--input",   default="data/access.log", help="Input log file / HDFS path")
    parser.add_argument("--output",  default="results/",        help="Output directory / HDFS path")
    parser.add_argument("--jobs",    default="all",             help="Comma-separated job IDs or 'all'")
    parser.add_argument("--streaming-jar",
                        default=os.environ.get("HADOOP_STREAMING_JAR",
                                               "$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar"),
                        help="Path to hadoop-streaming JAR")
    args = parser.parse_args()

    if not args.local and not args.hadoop:
        print("Specify --local or --hadoop"); sys.exit(1)

    # Filter jobs
    selected = JOBS if args.jobs == "all" else [
        j for j in JOBS if j["id"] in args.jobs.split(",")
    ]

    if args.local:
        os.makedirs(args.output, exist_ok=True)
        if not os.path.exists(args.input):
            print(f"Input file not found: {args.input}")
            print("Run:  python3 data/generate_sample_logs.py  to create sample data.")
            sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  Hadoop Web Log Analysis – {len(selected)} Jobs")
    print(f"  Mode  : {'LOCAL' if args.local else 'HADOOP'}")
    print(f"  Input : {args.input}")
    print(f"  Output: {args.output}")
    print(f"{'='*60}\n")

    total_ok, total_fail = 0, 0
    wall_start = time.time()

    for i, job in enumerate(selected, 1):
        print(f"[{i:02d}/{len(selected):02d}] {job['name']}")
        if args.local:
            ok, elapsed = run_local(job, args.input, args.output)
        else:
            ok, elapsed = run_hadoop(job, args.input, args.output, args.streaming_jar)
        (total_ok if ok else total_fail).__class__  # just for linting
        if ok: total_ok += 1
        else:  total_fail += 1

    wall = time.time() - wall_start
    print(f"\n{'='*60}")
    print(f"  Done in {wall:.1f}s  ✓ {total_ok} succeeded  ✗ {total_fail} failed")
    print(f"  Results → {args.output}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
