# Minimal Flink image for the SQL session-cluster path (arm64-friendly: no PyFlink).
# JVM-native Flink + the Kafka SQL connector + the failure-stats SQL. Used by the session cluster
# (JobManager/TaskManager) and the sql-client submitter.
FROM flink:1.19-java17

ADD https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.2.0-1.19/flink-sql-connector-kafka-3.2.0-1.19.jar \
    /opt/flink/lib/flink-sql-connector-kafka.jar
RUN chmod 644 /opt/flink/lib/flink-sql-connector-kafka.jar

COPY sql /opt/sql
