FROM bitnami/spark:latest

USER root

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Download MongoDB Spark Connector
RUN apt-get update && apt-get install -y curl

RUN mkdir -p /opt/spark/jars && \
    curl -o /opt/spark/jars/mongo-spark-connector_2.12-10.4.0.jar \
    https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.1.1/mongo-spark-connector_2.12-10.4.0.jar


# Add wait-for-it script to wait for services to be ready
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

# Copy all application files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
SPARK_EXTRA_CLASSPATH=/opt/spark/jars/mongo-spark-connector_2.12-10.4.1.jar

# Expose any necessary ports
EXPOSE 8888

# Default command (can be overridden in docker-compose)

CMD ["sleep", "infinity"]