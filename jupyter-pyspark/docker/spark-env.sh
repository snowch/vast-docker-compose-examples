SPARK_MASTER_WEBUI_PORT=1234
SPARK_DAEMON_CLASSPATH="/usr/local/spark/*"
SPARK_DAEMON_JAVA_OPTS="-DSPARK_LOGS_DIR=\$SPARK_LOGS_DIR -DSPARK_ROLE=\$SPARK_ROLE -XX:+HeapDumpOnOutOfMemoryError"

