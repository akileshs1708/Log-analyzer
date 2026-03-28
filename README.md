# Hadoop Log Analysis — Docker Setup

Run the full **Hadoop Web Server Log Analysis** in Docker with zero local setup.

---

## Project Structure

```
docker-project/
├── Dockerfile                  # Python 3.11 + Java 17 + Hadoop 3.3.6
├── docker-compose.yml          # Two services: local mode and Hadoop mode
├── docker-entrypoint.sh        # Boot: generate logs → run jobs → Streamlit
├── .dockerignore
├── hadoop-config/
│   ├── core-site.xml           # fs.defaultFS = hdfs://localhost:9000
│   ├── hdfs-site.xml           # dfs.replication = 1 (pseudo-distributed)
│   ├── mapred-site.xml         # mapreduce.framework.name = yarn
│   └── yarn-site.xml           # YARN settings + web UI on 0.0.0.0
└── hadoop_log_analysis/
    ├── data/
    │   ├── generate_sample_logs.py   # Creates 50,000-line access.log
    │   └── access.log                # Auto-generated on first boot
    ├── mapreduce/
    │   ├── log_parser.py             # Shared Apache Combined Log parser
    │   ├── mapper/                   # 13 mapper scripts (q01–q13)
    │   └── reducer/                  # 13 reducer scripts (q01–q13)
    ├── scripts/
    │   └── run_all_jobs.py           # Orchestrator (--local or --hadoop)
    ├── streamlit_app/
    │   └── app.py                    # 7-page interactive Streamlit dashboard
    ├── results/                      # TSV outputs from each MapReduce job
    └── requirements.txt
```

---

## Quick Start

### Option 1 — Local Mode (fast, ~30 seconds, no Hadoop cluster)

Runs all 13 MapReduce jobs using Unix pipes:

```bash
docker compose up log-analysis-local
```

Open: **http://localhost:8501**

---

### Option 2 — Full Hadoop Mode (pseudo-distributed HDFS + YARN)

Starts HDFS + YARN, uploads log to HDFS, runs all 13 Streaming jobs, then launches the dashboard:

```bash
docker compose up log-analysis-hadoop
```

| Interface              | URL                   |
|------------------------|-----------------------|
| Streamlit Dashboard    | http://localhost:8501 |
| HDFS NameNode UI       | http://localhost:9870 |
| YARN ResourceManager   | http://localhost:8088 |

> Hadoop mode requires at least **4 GB RAM** allocated to Docker.

---

## Environment Variables

| Variable    | Default  | Description                                              |
|-------------|----------|----------------------------------------------------------|
| `MODE`      | `local`  | `local` = Unix pipes · `hadoop` = Hadoop Streaming       |
| `SKIP_JOBS` | `false`  | `true` = skip job execution, serve existing results      |


## The 13 Analysis Jobs

| ID  | Question                                    |
|-----|---------------------------------------------|
| Q01 | Requests per IP address                     |
| Q02 | Most requested URLs                         |
| Q03 | Requests per day and per hour               |
| Q04 | HTTP status code distribution               |
| Q05 | Bandwidth consumed per URL                  |
| Q06 | Top error-generating URLs (4xx/5xx)         |
| Q07 | HTTP method distribution (GET/POST/…)       |
| Q08 | Browser family breakdown                    |
| Q09 | Device type breakdown (Desktop/Mobile/Bot)  |
| Q10 | Average response time per URL               |
| Q11 | Top referrer domains                        |
| Q12 | Hourly traffic pattern (hours 0–23)        |
| Q13 | Suspicious / attack IP detection            |

---

## Useful Commands

```bash
# Exec into running container
docker exec -it hadoop-log-analysis-local bash

# Re-run a single job manually inside the container
cd /app
python3 mapreduce/mapper/q01_ip_requests_mapper.py < data/access.log \
  | sort \
  | python3 mapreduce/reducer/q01_ip_requests_reducer.py \
  > results/q01_ip_requests.tsv

# Reset everything (removes volumes)
docker compose down -v
```

---

## Tech Stack

| Component         | Version      |
|-------------------|--------------|
| Python            | 3.11-bullseye|
| Java              | OpenJDK 11   |
| Hadoop            | 3.3.6        |
| Streamlit         | >= 1.32      |
| Plotly            | >= 5.18      |
| Pandas            | >= 2.0       |
