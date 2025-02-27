#!/usr/bin/env python3

import os
import json
import time
import praw
from confluent_kafka import Producer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API configuration
reddit_client_id = os.getenv('CLIENT_ID')
reddit_client_secret = os.getenv('CLIENT_SECRET')
reddit_user_agent = os.getenv('USER_AGENT')
reddit_username = os.getenv('USERNAME')
reddit_password = os.getenv('PASSWORD')


# Kafka configuration
kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
kafka_topic = os.getenv('KAFKA_TOPIC', 'redditstream')

class RedditProducer:
    def __init__(self):
        """Initialize the Reddit API client and Kafka producer"""
        # Initialize Reddit API client
        self.reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent,
            username=reddit_username,
            password=reddit_password
        )

        # Wait for Kafka to be available
        self._wait_for_kafka()
        
        # Initialize Confluent Kafka Producer
        self.producer = Producer({
            'bootstrap.servers': kafka_bootstrap_servers,
            'acks': 'all',
            'retries': 3,
            'retry.backoff.ms': 100
        })
        
        print(f" Connected to Kafka at {kafka_bootstrap_servers}")

    def _wait_for_kafka(self, max_retries=30, wait_time=5):
        """Wait until Kafka is available"""
        retry_count = 0
        while retry_count < max_retries:
            try:
                test_producer = Producer({'bootstrap.servers': kafka_bootstrap_servers})
                test_producer.list_topics(timeout=5)
                print("Successfully connected to Kafka")
                return
            except Exception as e:
                print(f"⚠️ Waiting for Kafka to be available... ({retry_count}/{max_retries})")
                retry_count += 1
                time.sleep(wait_time)
        
        raise Exception(" Failed to connect to Kafka after multiple retries")

    def delivery_report(self, err, msg):
        """Delivery callback for Kafka messages"""
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message sent to Kafka topic {msg.topic()}")

    def stream_reddit_posts(self, subreddit_name='all', limit=None, sleep_time=2):
        """Stream posts from a specified subreddit"""
        print(f" Streaming posts from r/{subreddit_name}...")

        subreddit = self.reddit.subreddit(subreddit_name)

        for submission in subreddit.stream.submissions():
            post_data = {
                'id': submission.id,
                'title': submission.title,
                'author': str(submission.author),
                'score': submission.score,
                'num_comments': submission.num_comments,
                'subreddit': submission.subreddit.display_name,
                'timestamp': time.time()
            }

            json_data = json.dumps(post_data).encode('utf-8')

            # Print data before sending it to Kafka
            print(" Sending Post to Kafka:")
            print(json.dumps(post_data, indent=4))

            # Send data to Kafka
            self.producer.produce(kafka_topic, value=json_data, callback=self.delivery_report)
            
            
            print("**"*100)

            # Flush the producer to ensure immediate delivery
            self.producer.flush()

            # Sleep to control data rate
            time.sleep(sleep_time)

            # Stop after the limit is reached
            if limit is not None:
                limit -= 1
                if limit <= 0:
                    break

    def close(self):
        """Close the Kafka producer"""
        if self.producer is not None:
            self.producer.flush()
            print("Kafka producer closed")


if __name__ == "__main__":
    producer = None
    try:
        producer = RedditProducer()
        
        # Configure the subreddit(s) you want to stream from
        subreddit_to_stream = os.getenv('REDDIT_SUBREDDIT', 'all')
        
        # Start streaming with a sleep time of 2 seconds between messages
        producer.stream_reddit_posts(subreddit_name=subreddit_to_stream, sleep_time=2)
        
    except KeyboardInterrupt:
        print(" Stopping Reddit Post Producer...")
    except Exception as e:
        print(f"Error in Reddit Producer: {e}")
    finally:
        if producer:
            producer.close()
