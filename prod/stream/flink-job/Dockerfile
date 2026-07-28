# Flink failure-statistics job image (ASC-031).
# Bundles the PyFlink job + SQL onto the Flink base so the operator can run it in application mode.
FROM flink:1.19-java17

# Python + PyFlink for the SQL/DataStream job.
RUN apt-get update -y \
 && apt-get install -y --no-install-recommends python3 python3-pip \
 && rm -rf /var/lib/apt/lists/* \
 && ln -sf /usr/bin/python3 /usr/bin/python
RUN pip3 install --no-cache-dir apache-flink==1.19.1

# Kafka SQL connector for the source/sink tables.
ADD https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.2.0-1.19/flink-sql-connector-kafka-3.2.0-1.19.jar \
    /opt/flink/lib/flink-sql-connector-kafka.jar

WORKDIR /opt/asc-flink
COPY sql ./sql
COPY pyflink ./pyflink

# Application-mode entrypoint; KAFKA_BOOTSTRAP is injected by the FlinkDeployment.
ENV KAFKA_BOOTSTRAP=kafka.data.svc.cluster.local:9092
