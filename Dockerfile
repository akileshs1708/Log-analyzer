FROM python:3.11-bullseye

# ── System dependencies ────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-11-jdk \
    wget \
    curl \
    ssh \
    rsync \
    procps \
    && rm -rf /var/lib/apt/lists/*

# ── Java env ───────────────────────────────────────────────────────────────────
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# ── Hadoop installation ────────────────────────────────────────────────────────
ENV HADOOP_VERSION=3.3.6
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib/native"
ENV HDFS_NAMENODE_USER=root
ENV HDFS_DATANODE_USER=root
ENV HDFS_SECONDARYNAMENODE_USER=root
ENV YARN_RESOURCEMANAGER_USER=root
ENV YARN_NODEMANAGER_USER=root

RUN wget -q "https://downloads.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz" \
    -O /tmp/hadoop.tar.gz \
    && tar -xzf /tmp/hadoop.tar.gz -C /opt \
    && mv /opt/hadoop-${HADOOP_VERSION} ${HADOOP_HOME} \
    && rm /tmp/hadoop.tar.gz

# ── SSH setup for Hadoop pseudo-distributed ────────────────────────────────────
RUN ssh-keygen -t rsa -P "" -f /root/.ssh/id_rsa \
    && cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys \
    && chmod 600 /root/.ssh/authorized_keys \
    && echo "Host localhost\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null" > /root/.ssh/config

# ── Hadoop XML configuration ───────────────────────────────────────────────────
COPY hadoop-config/core-site.xml     $HADOOP_CONF_DIR/core-site.xml
COPY hadoop-config/hdfs-site.xml     $HADOOP_CONF_DIR/hdfs-site.xml
COPY hadoop-config/mapred-site.xml   $HADOOP_CONF_DIR/mapred-site.xml
COPY hadoop-config/yarn-site.xml     $HADOOP_CONF_DIR/yarn-site.xml

RUN echo "export JAVA_HOME=${JAVA_HOME}" >> $HADOOP_CONF_DIR/hadoop-env.sh

# ── Python dependencies ────────────────────────────────────────────────────────
WORKDIR /app
COPY hadoop_log_analysis/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application code ───────────────────────────────────────────────────────────
COPY hadoop_log_analysis/ /app/

# ── Entrypoint ─────────────────────────────────────────────────────────────────
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8501 9870 8088

ENV PYTHONPATH=/app

ENTRYPOINT ["/docker-entrypoint.sh"]
