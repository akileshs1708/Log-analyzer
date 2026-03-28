#!/bin/bash
# =============================================================================
# docker-entrypoint.sh – Boot Hadoop + run jobs + launch Streamlit dashboard
# =============================================================================
set -euo pipefail

MODE="${MODE:-local}"   # "local" or "hadoop"
SKIP_JOBS="${SKIP_JOBS:-false}"  # set to "true" to use pre-built results

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
log()  { echo -e "${GREEN}[BOOT]${NC} $*"; }
info() { echo -e "${CYAN}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }

log "======================================================="
log "  🪵  Hadoop Log Analysis – Docker Container"
log "  Mode: ${MODE}"
log "======================================================="

# ── Generate sample logs if missing ───────────────────────────────────────────
if [ ! -f /app/data/access.log ]; then
    log "Generating sample access logs (50,000 entries)..."
    python3 /app/data/generate_sample_logs.py
    log "Log generation complete: $(wc -l < /app/data/access.log) lines"
else
    log "Found existing access.log: $(wc -l < /app/data/access.log) lines"
fi

# ── Run MapReduce jobs ─────────────────────────────────────────────────────────
mkdir -p /app/results

if [ "$SKIP_JOBS" = "true" ]; then
    warn "SKIP_JOBS=true – skipping MapReduce job execution, using existing results"
elif [ "$MODE" = "hadoop" ]; then
    # ── Start SSH daemon (needed by Hadoop) ────────────────────────────────────
    log "Starting SSH daemon..."
    service ssh start || true
    export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
    export HADOOP_HOME=/opt/hadoop
    export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
    export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
    chmod -R 777 /tmp
    chmod -R 777 /tmp/hadoop-data
    # ── Format HDFS (first time only) ─────────────────────────────────────────
    if [ ! -d /tmp/hadoop-data/namenode ]; then
        log "Formatting HDFS namenode..."
        $HADOOP_HOME/bin/hdfs namenode -format -nonInteractive -force
    fi
    
    # ── Start HDFS ─────────────────────────────────────────────────────────────
    log "Starting HDFS..."
    $HADOOP_HOME/sbin/start-dfs.sh
    sleep 5

    # ── Start YARN ─────────────────────────────────────────────────────────────
    
    log "Starting YARN..."
    $HADOOP_HOME/sbin/start-yarn.sh
    sleep 5
    jps
    
    # ── Wait for NameNode to leave safe mode ───────────────────────────────────
    log "Waiting for NameNode to exit safe mode..."
    $HADOOP_HOME/bin/hdfs dfsadmin -safemode wait || true

    # ── Create HDFS dirs & upload log ─────────────────────────────────────────
    log "Setting up HDFS directories..."
    $HADOOP_HOME/bin/hdfs dfs -mkdir -p /user/root /logs/input /logs/results
    $HADOOP_HOME/bin/hdfs dfs -put -f /app/data/access.log /logs/input/access.log

    # ── Find Streaming JAR ─────────────────────────────────────────────────────
    STREAMING_JAR=$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar
    export HADOOP_STREAMING_JAR="$STREAMING_JAR"
    log "Streaming JAR: $STREAMING_JAR"

    # ── Run all 13 jobs via Hadoop Streaming ───────────────────────────────────
    log "Running all 13 MapReduce jobs via Hadoop Streaming..."
    cd /app && python3 scripts/run_all_jobs.py \
        --hadoop \
        --input  hdfs:///logs/input/access.log \
        --output hdfs:///logs/results/ \
        --streaming-jar "$STREAMING_JAR"

    # ── Fetch results from HDFS ────────────────────────────────────────────────
    log "Fetching results from HDFS..."
    for job in q01_ip_requests q02_url_requests q03_time_requests q04_status_codes \
               q05_bandwidth q06_error_urls q07_http_methods q08_browsers q09_devices \
               q10_response_time q11_referrers q12_hourly_pattern q13_suspicious_ips; do
        $HADOOP_HOME/bin/hdfs dfs -getmerge /logs/results/${job} /app/results/${job}.tsv || true
    done
    log "All results fetched to /app/results/"

else
    # ── LOCAL mode (default, fast, no Hadoop) ─────────────────────────────────
    log "Running all 13 MapReduce jobs in LOCAL mode..."
    cd /app && python3 scripts/run_all_jobs.py \
        --local \
        --input  data/access.log \
        --output results/
    log "All jobs complete!"
fi

# ── Launch Streamlit ───────────────────────────────────────────────────────────
info ""
info "======================================================="
info "  ✅  Setup complete!"
info ""
info "  📊 Streamlit Dashboard → http://localhost:8501"
if [ "$MODE" = "hadoop" ]; then
    info "  🐘 HDFS NameNode UI  → http://localhost:9870"
    info "  🧵 YARN ResourceMgr  → http://localhost:8088"
fi
info "======================================================="
info ""

cd /app
exec streamlit run streamlit_app/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
