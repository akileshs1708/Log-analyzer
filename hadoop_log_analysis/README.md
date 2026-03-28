# Hadoop Web Server Log Analysis

Analyzing Apache/Nginx access logs at scale using **Hadoop MapReduce** (Python + Hadoop Streaming),
with a **Streamlit** dashboard to visualize all results.

---

## Project Structure

```
hadoop_log_analysis/
├── data/
│   ├── generate_sample_logs.py    # Generates realistic Apache log data (50k lines)
│   └── access.log                 # Generated sample log file
│
├── mapreduce/
│   ├── log_parser.py              # Shared log parser (Combined Log Format)
│   ├── mapper/
│   │   ├── q01_ip_requests_mapper.py
│   │   ├── q02_url_requests_mapper.py
│   │   ├── q03_time_requests_mapper.py
│   │   ├── q04_status_codes_mapper.py
│   │   ├── q05_bandwidth_mapper.py
│   │   ├── q06_error_urls_mapper.py
│   │   ├── q07_http_methods_mapper.py
│   │   ├── q08_browser_mapper.py
│   │   ├── q09_device_mapper.py
│   │   ├── q10_response_time_mapper.py
│   │   ├── q11_referrer_mapper.py
│   │   ├── q12_hourly_pattern_mapper.py
│   │   └── q13_suspicious_ip_mapper.py
│   └── reducer/
│       └── (same pattern, q01–q13)
│
├── scripts/
│   ├── run_all_jobs.py            # Master job runner (local or Hadoop mode)
│   └── setup_hadoop.sh            # Hadoop pseudo-distributed setup + HDFS upload
│
├── streamlit_app/
│   └── app.py                     # Full dashboard (6 pages, 13 analysis views)
│
├── results/                       # TSV output from each MapReduce job
├── requirements.txt
└── README.md
```

---

## The 13 Analysis Questions

| # | Question | MapReduce Job |
|---|----------|---------------|
| Q01 | How many requests per IP address? | `q01_ip_requests` |
| Q02 | What are the most requested URLs? | `q02_url_requests` |
| Q03 | How many requests per day / per hour? | `q03_time_requests` |
| Q04 | HTTP status code distribution (200/404/500…)? | `q04_status_codes` |
| Q05 | Which URLs consume the most bandwidth? | `q05_bandwidth` |
| Q06 | Which URLs generate the most errors (4xx/5xx)? | `q06_error_urls` |
| Q07 | HTTP method distribution (GET/POST/PUT/DELETE)? | `q07_http_methods` |
| Q08 | Which browser families are most common? | `q08_browsers` |
| Q09 | Device type breakdown (Desktop/Mobile/Tablet/Bot)? | `q09_devices` |
| Q10 | Average response time per URL? | `q10_response_time` |
| Q11 | Top traffic referrer domains? | `q11_referrers` |
| Q12 | Hourly traffic pattern across the day (0–23)? | `q12_hourly_pattern` |
| Q13 | Which IPs show suspicious/attack behavior? | `q13_suspicious_ips` |

---


## Dashboard Pages

| Page | Content |
|------|---------|
| 📊 Overview | KPIs, daily traffic, status pie, top IPs & URLs, jobs summary table |
| 🌐 Traffic Analysis | Q01 IP table, Q02 URLs, Q03 time series, Q05 bandwidth |
| ⚠️ Errors & Status | Q04 status codes (pie + class grouping), Q06 error URLs |
| 👤 Clients & Devices | Q07 methods, Q08 browsers, Q09 devices, Q11 referrers |
| ⚡ Performance | Q10 response times (bar + scatter), Q12 hourly heatmap |
| 🔴 Security | Q13 suspicious IPs (stacked bars, scatter, risk table) |
| 📁 Raw Results | Browse + download any TSV result file |

---

## Tech Stack

```
HDFS          → Distributed file storage for logs and results
YARN          → Cluster resource manager (schedules MapReduce jobs)
Hadoop Streaming → Bridge between Hadoop and Python scripts
Python 3      → MapReduce logic (mapper + reducer scripts)
log_parser.py → Regex-based Combined Log Format parser (shared module)
Streamlit     → Interactive web dashboard
Plotly        → Charts (bar, pie, line, scatter, area)
Pandas        → TSV result loading and manipulation
```
