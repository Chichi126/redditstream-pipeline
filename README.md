
## This is a project that shows streaming of data from Reddit using the Reddit API with Kafka and using Spark to transform and load the messages into MongoDB, a NoSQL Database

![](https://github.com/Chichi126/reddit_kafka_spark/blob/715b029dac1eba80683ff188a70f4d668800966c/Screenshot%202024-12-16%20at%209.59.01%20AM.png)


# Reddit Data Pipeline Project

## Project Overview
This project implements a robust data pipeline that:
- Fetches data from the Reddit API
- Streams data using Apache Kafka
- Processes data with Apache Spark
- Stores processed data in MongoDB
- Uses Docker for containerization and service management

## Prerequisites
- Docker
- Docker Compose
- Python 3.8+
- Reddit API Credentials

## Project Structure

redditstream-pipeline/
│

├── Dockerfile

├── requirements.txt

├── docker-compose.yml

├── producer.py

├── consumer.py

└── README.md

## Setup and Configuration

### 1. Reddit API Credentials
1. Create a Reddit Developer Account
2. Create a new application in Reddit's developer portal
3. Obtain:
   - Client ID
   - Client Secret
   - User Agent
   - Reddit Username
   - Reddit Password

### 2. Environment Configuration
Create a `.env` file in the project root with the following variables:
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

KAFKA_BOOTSTRAP_SERVERS=kafka:9092
MONGODB_CONNECTION_STRING=mongodb://mongodb:27017/
```

# Reddit Data Pipeline Project

## Project Overview
This project implements a data pipeline that:
- Fetches data from the Reddit API
- Streams data using Apache Kafka
- Processes data with Apache Spark
- Stores processed data in MongoDB
- Uses Docker for containerization and service management

## Prerequisites
- Docker
- Docker Compose
- Python 3.8+
- Reddit API Credentials

## Project Structure
```
reddit-data-pipeline/
│
├── Dockerfile
├── requirements.txt
├── docker-compose.yml
├── producer.py
├── consumer.py
└── README.md
```

## Setup and Configuration

### 1. Reddit API Credentials
1. Create a Reddit Developer Account
2. Create a new application in Reddit's developer portal
3. Obtain:
   - Client ID
   - Client Secret
   - User Agent
   - Reddit Username
   - Reddit Password

### 2. Environment Configuration
Create a `.env` file in the project root with the following variables:
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

KAFKA_BOOTSTRAP_SERVERS=kafka:9092
MONGODB_CONNECTION_STRING=mongodb://mongodb:27017/
```



## Step 2: Setting Up Docker Compose

Docker Compose was used to spin up Kafka, Spark, and MongoDB services. Here's an outline of the configuration:

##### Kafka Setup:

Zookeeper and Kafka brokers were defined in the docker-compose.yml file.

A Kafka topic was pre-configured using a Confluent control center or command-line tools.



##### MongoDB Setup:

MongoDB was set up in Docker with a mapped volume to persist data.

Authentication and networking settings were properly configured for external clients to access.

##### Spark Setup:

Spark master and worker nodes were defined using proper networking.

Spark image was pulled with the necessary connectors for Kafka and MongoDB pre-installed.


![HERE](docker-compose.yml)


## Running the Project

### 1. Build Docker Images
```bash
docker-compose --build
```

### 2. Start Services
```bash
docker-compose up -d
```

### 3. Monitor Logs
```bash
docker-compose logs -f
```

### 4. Stop Services
```bash
docker-compose down
```

## Core Components

### Reddit Producer
- Authenticates with Reddit API
- Fetches Reddit posts/comments
- Publishes data to Kafka topic

## Step 3: Writing the Streaming Application

The Python application reads data from Kafka, processes it using Spark, and writes it to MongoDB. 

#### Key components:

*Kafka Integration:*

Spark reads the data stream from Kafka using the Kafka-Spark connector.

The Kafka topic is subscribed to, and data is read in JSON format.

To create a kafka topic (using kafka confluent)

Note that if /bin/sh doesn’t give you access to the required tools, try using /bin/bash instead



Here is the python code for the producer to stream data from Reddit Api ![producer.py](HERE)

### 3. Monitor Logs
```bash
docker-compose logs -f reddit-producer
```


### Spark Consumer
- Consumes messages from Kafka
- Transforms and cleanses data
- Loads processed data into MongoDB


*Data Transformation:*

The data stream is processed using PySpark DataFrame APIs.

Schema definitions ensure proper parsing of JSON data.

*Writing to MongoDB:*

Data is written to MongoDB using the MongoDB-Spark connector.

Each micro-batch is appended to a specified database and collection.

#### Subscribing using spark and writing to Mongodb

Here is the link to the consumer python ![consumer.py](here)

### 3. Monitor Logs
```bash
docker-compose logs -f spark-consumer
```


## Monitoring and Debugging
- Check Kafka topics: `docker-compose exec kafka kafka-topics.sh --list --zookeeper zookeeper:2181`
- View MongoDB data: `docker-compose exec mongodb mongo`

