## This is a project that shows streaming of data from Reddit using the Reddit API with Kafka and using Spark to transfrom and load the messages into MongoDB a NoSQL Database


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
```
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

### 3. Project Dependencies
#### Reddit Producer (requirements.txt)
```
praw
kafka-python
python-dotenv
```

#### Spark Consumer (requirements.txt)
```
pyspark
pymongo
kafka-python
python-dotenv
```

### 4. Dockerfiles

#### Reddit Producer Dockerfile
```dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "producer.py"]
```

#### Spark Consumer Dockerfile
```dockerfile
FROM jupyter/pyspark-notebook

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "consumer.py"]
```

### 5. Docker Compose Configuration
```yaml
version: '3'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    ports:
      - "2181:2181"

  kafka:
    image: wurstmeister/kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_ADVERTISED_HOST_NAME: kafka
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    depends_on:
      - zookeeper

  mongodb:
    image: mongo
    ports:
      - "27017:27017"

  reddit-producer:
    build: ./reddit-producer
    env_file: .env
    depends_on:
      - kafka

  spark-consumer:
    build: ./spark-consumer
    env_file: .env
    depends_on:
      - kafka
      - mongodb
```

## Running the Project

### 1. Build Docker Images
```bash
docker-compose build
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

### Spark Consumer
- Consumes messages from Kafka
- Transforms and cleanses data
- Loads processed data into MongoDB

## Monitoring and Debugging

- Check Kafka topics: `docker-compose exec kafka kafka-topics.sh --list --zookeeper zookeeper:2181`
  
- View MongoDB data: `docker-compose exec mongodb mongo`


## Troubleshooting

- Ensure all environment variables are correctly set
- 
- Check network connectivity between containers
- 
- Verify Reddit API credentials


