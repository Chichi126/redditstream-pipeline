#!/usr/bin/env python3

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Kafka configuration
kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
kafka_topic = os.getenv('KAFKA_TOPIC', 'redditstream')

# MongoDB configuration
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_DB = os.getenv("MONGODB_DATABASE")
MONGO_COLLECTION = os.getenv("MONGODB_COLLECTION")

# MongoDB URI for Spark - Corrected format
MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}/{MONGO_DB}?retryWrites=true&w=majority"


class SparkConsumer:
    def __init__(self):
        """Initialize Spark session"""
        self.spark = SparkSession.builder \
            .appName("RedditStreamProcessor") \
            .master("spark://spark-master:7077") \
            .config("spark.jars.packages", 
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,"
                    "org.mongodb.spark:mongo-spark-connector_2.12:10.4.0") \
            .config("spark.mongodb.connection.uri", MONGO_URI) \
            .config("spark.mongodb.database", MONGO_DB) \
            .config("spark.mongodb.collection", MONGO_COLLECTION) \
            .config("spark.mongodb.write.connection.timeout.ms", "30000") \
            .config("spark.mongodb.read.connection.timeout.ms", "30000") \
            .config("spark.mongodb.operation.timeout.ms", "30000") \
            .getOrCreate()

        self.spark.sparkContext.setLogLevel("WARN")
        
        # Define schema for the Reddit posts
        self.reddit_schema = StructType([
            StructField("id", StringType(), True),
            StructField("title", StringType(), True),
            StructField("author", StringType(), True),
            StructField("subreddit", StringType(), True),
            StructField("score", IntegerType(), True),
            StructField("num_comments", IntegerType(), True),
            StructField("timestamp", DoubleType(), True)
        ])
        
        print("Spark session initialized")
        self.test_mongo_connection()

    def test_mongo_connection(self):
        """Test MongoDB connection by writing a small test dataframe"""
        try:
            # Create a small test dataframe
            test_df = self.spark.createDataFrame([("connection_test",)], ["test"])
            test_df.write \
                .format("mongodb") \
                .mode("append") \
                .option("database", MONGO_DB) \
                .option("collection", "connection_test") \
                .save()
            print("MongoDB connection successful")
            return True
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            return False
    
    def test_kafka_connection(self):
        """Test Kafka connection by checking if broker is reachable"""
        try:
            # Import socket to check connectivity
            import socket
            
            # Parse host and port from bootstrap servers
            host, port_str = kafka_bootstrap_servers.split(':')
            port = int(port_str)
            
            # Try to connect to the Kafka broker
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 second timeout
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"Kafka connection successful. Server {kafka_bootstrap_servers} is reachable.")
                return True
            else:
                print(f"Kafka connection failed. Server {kafka_bootstrap_servers} is not reachable.")
                return False
        except Exception as e:
            print(f"Kafka connection test failed: {e}")
            return False

    def process_stream(self):
        """Process the stream of Reddit posts from Kafka and store in MongoDB"""
        try:
            # Test connections before starting the stream
            kafka_ok = self.test_kafka_connection()
            mongo_ok = self.test_mongo_connection()
            
            if not mongo_ok:
                raise Exception("Could not connect to MongoDB. Please check your configuration.")
            
            if not kafka_ok:
                raise Exception("Could not connect to Kafka. Please check your configuration.")
            
            # Read stream from Kafka
            kafka_stream = self.spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
                .option("subscribe", kafka_topic) \
                .option("startingOffsets", "earliest") \
                .option("failOnDataLoss", "false") \
                .load()
            
            # Parse JSON data and select needed fields
            parsed_stream = kafka_stream \
                .select(from_json(col("value").cast("string"), self.reddit_schema).alias("data")) \
                .select("data.*")

            parsed_stream.printSchema()

            # Add processing timestamp
            transformed_stream = parsed_stream \
                .withColumn("processing_time", current_timestamp())
            
            # Function to write each micro-batch to MongoDB and print to console
            def write_to_mongo_and_print(batch_df, batch_id):
                if batch_df.count() > 0:  # Only process non-empty batches
                    print(f"Processing batch ID: {batch_id} with {batch_df.count()} records")
                    batch_df.show(truncate=False)  # Print DataFrame to console
                    
                    try:
                        batch_df.write \
                            .format("mongodb") \
                            .mode("append") \
                            .option("database", MONGO_DB) \
                            .option("collection", MONGO_COLLECTION) \
                            .save()
                        print(f"Successfully wrote batch {batch_id} to MongoDB")
                    except Exception as e:
                        print(f"Error writing batch {batch_id} to MongoDB: {e}")
                else:
                    print(f"Skipping empty batch {batch_id}")

            # Use foreachBatch to write data to MongoDB and print to console
            query = transformed_stream.writeStream \
                .foreachBatch(write_to_mongo_and_print) \
                .outputMode("append") \
                .option("checkpointLocation", "/tmp/mongo_checkpoint") \
                .start()
            
            print("Stream processing started")
            query.awaitTermination()
        
        except Exception as e:
            print(f"Error in Spark consumer: {e}")
            raise e
        finally:
            self.spark.stop()
            print("Spark session stopped")

if __name__ == "__main__":
    try:
        spark_consumer = SparkConsumer()
        spark_consumer.process_stream()
    except Exception as e:
        print(f"Failed to start or run Spark consumer: {e}")