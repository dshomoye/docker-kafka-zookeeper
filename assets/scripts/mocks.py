import os
import sys
import threading
import time
from typing import List

from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import NoBrokersAvailable, TopicAlreadyExistsError

bootstrap_servers = "localhost:9092"
topics_key = "CREATE_TOPICS"
consumers_key = "CREATE_CONSUMERS"
producers_key = "CREATE_PRODUCERS"
unavailable_retries = 5

def get_admin_client() -> KafkaAdminClient:
    return KafkaAdminClient(bootstrap_servers=bootstrap_servers, client_id="mocks")


def create_topic(name: str, client: KafkaAdminClient) -> None:
    try:
        client.create_topics([NewTopic(name, 1, 1)])
    except TopicAlreadyExistsError:
        return
    return

def start_consumer(topic: str, group: str) -> None:
    print(f"consumer {group} consuming {topic}")
    consumer = KafkaConsumer(topic, group_id=group, bootstrap_servers=[bootstrap_servers])
    for _ in consumer:
        time.sleep(1)

def start_producer(topics: List[str]) -> None:
    producer = KafkaProducer(bootstrap_servers=[bootstrap_servers])
    print(f"producing to topic: {topics}")
    while True:
        time.sleep(1)
        for t in topics:
            producer.send(t, b"hello world")


def start():
    runners = []
    print("getting admin client")
    admin_client = get_admin_client()
    topics_str = os.getenv(topics_key)
    topics = topics_str.split(",") if topics_str else []
    print(f"creating topics {topics}")
    for topic in topics:
        create_topic(topic, admin_client)
    producers_string = os.getenv(producers_key)
    producers = producers_string.split(";") if producers_string else []
    for pr in producers:
        _, t = pr.split(":")
        p_topics = t.split(",")
        t = threading.Thread(target=start_producer, args=(p_topics,))
        t.start()
        runners.append(t)
    consumers_string = os.getenv(consumers_key)
    consumers = consumers_string.split(";") if consumers_string else []
    for c in consumers:
        consumer, t = c.split(":")
        c_topics = t.split(",")
        for c_t in c_topics:
            t = threading.Thread(target=start_consumer, args=(c_t, consumer))
            t.start()
            runners.append(t)
    return runners


def main():
    global unavailable_retries
    try:
        runners = start()
        for r in runners:
            r.join()
    except NoBrokersAvailable:
        if unavailable_retries:
            print("no brokers available trying again in 5s...")
            time.sleep(5)
            unavailable_retries -= 1
            main()
        print("Unable to connect to any brokers. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"exception: {str(e)}")

if __name__ == "__main__":
    main()
