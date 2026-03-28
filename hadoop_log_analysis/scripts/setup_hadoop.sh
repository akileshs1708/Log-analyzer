#!/usr/bin/env bash
# =============================================================================
# setup_hadoop.sh – Configure Hadoop pseudo-distributed mode & upload logs
# =============================================================================
# Prerequisites: Java 8+, Hadoop 3.x installed and HADOOP_HOME set
# Run: chmod +x setup_hadoop.sh && ./setup_hadoop.sh
# =============================================================================

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log()  { echo -e "${GREEN}[SETUP]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $*"; }
die()  { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ── 1. Validate environment ───────────────────────────────────────────────────
log "Checking prerequisites..."
[[ -z "${HADOOP_HOME:-}" ]] && die "HADOOP_HOME is not set. Export it before running."
[[ -z "${JAVA_HOME:-}" ]]   && die "JAVA_HOME is not set."
command -v python3 >/dev/null || die "python3 not found"

log "HADOOP_HOME = $HADOOP_HOME"
log "JAVA_HOME   = $JAVA_HOME"

# ── 2. Generate sample logs if missing ───────────────────────────────────────
LOG_FILE="data/access.log"
if [[ ! -f "$LOG_FILE" ]]; then
    log "Generating sample access logs..."
    python3 data/generate_sample_logs.py
else
    log "Log file already exists: $LOG_FILE ($(wc -l < "$LOG_FILE") lines)"
fi

# ── 3. Find Hadoop Streaming JAR ─────────────────────────────────────────────
STREAMING_JAR=$(find "$HADOOP_HOME" -name "hadoop-streaming-*.jar" 2>/dev/null | head -1)
[[ -z "$STREAMING_JAR" ]] && die "hadoop-streaming JAR not found under $HADOOP_HOME"
log "Streaming JAR: $STREAMING_JAR"
export HADOOP_STREAMING_JAR="$STREAMING_JAR"

# ── 4. Format namenode (first-time setup) ─────────────────────────────────────
HDFS_DIR="$HOME/.hadoop_formatted"
if [[ ! -f "$HDFS_DIR" ]]; then
    warn "Formatting HDFS namenode (first time only)..."
    "$HADOOP_HOME/bin/hdfs" namenode -format -nonInteractive
    touch "$HDFS_DIR"
    log "Namenode formatted."
fi

# ── 5. Start HDFS & YARN ──────────────────────────────────────────────────────
log "Starting HDFS..."
"$HADOOP_HOME/sbin/start-dfs.sh"

log "Starting YARN..."
"$HADOOP_HOME/sbin/start-yarn.sh"

# ── 6. Create HDFS directories ───────────────────────────────────────────────
log "Creating HDFS directories..."
"$HADOOP_HOME/bin/hdfs" dfs -mkdir -p /user/"$USER"
"$HADOOP_HOME/bin/hdfs" dfs -mkdir -p /logs/input
"$HADOOP_HOME/bin/hdfs" dfs -mkdir -p /logs/results

# ── 7. Upload log file to HDFS ───────────────────────────────────────────────
log "Uploading $LOG_FILE → hdfs:///logs/input/"
"$HADOOP_HOME/bin/hdfs" dfs -put -f "$LOG_FILE" /logs/input/access.log
log "HDFS upload complete."
"$HADOOP_HOME/bin/hdfs" dfs -ls /logs/input/

# ── 8. Print next steps ───────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "  Setup complete! Run jobs with:"
echo ""
echo "  # Local mode (fast, no Hadoop needed):"
echo "  python3 scripts/run_all_jobs.py --local --input data/access.log --output results/"
echo ""
echo "  # Hadoop mode:"
echo "  python3 scripts/run_all_jobs.py --hadoop \\"
echo "      --input hdfs:///logs/input/access.log \\"
echo "      --output hdfs:///logs/results/"
echo ""
echo "  # Then launch dashboard:"
echo "  streamlit run streamlit_app/app.py"
echo "============================================================"
