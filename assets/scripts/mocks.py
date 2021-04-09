import os
import time
from typing import List
from multiprocessing import Process

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable

bootstrap_servers = "localhost:9092"
consumers_key = "MOCK_CONSUMERS"
producers_key = "MOCK_PRODUCERS"
unavailable_retries = 5

def start_consumer(topic: str, group: str) -> None:
    retries = unavailable_retries
    while retries:
        try:
            consumer = KafkaConsumer(topic, group_id=group, bootstrap_servers=[bootstrap_servers])
            print(f"consumer {group} consuming {topic}")
            for _ in consumer:
                time.sleep(1)
        except NoBrokersAvailable:
            time.sleep(5)
            retries -= 1
    print(f"unable to create consumer {group}, broker unreachable")


def start_producer(topics: List[str]) -> None:
    retries = unavailable_retries
    while retries:
        try:
            producer = KafkaProducer(bootstrap_servers=[bootstrap_servers])
            print(f"producing to topic: {topics}")
            while True:
                time.sleep(1)
                for t in topics:
                    producer.send(t, b"hello world")
        except NoBrokersAvailable:
            time.sleep(5)
            retries -= 1
    print(f"unable to create producer for {topics}, broker unreachable")


def start():    
    processes: List[Process] = []
    producers_string = os.getenv(producers_key)
    producers = producers_string.split(";") if producers_string else []
    for pr in producers:
        _, t = pr.split(":")
        p_topics = t.split(",")
        p = Process(target=start_producer, args=(p_topics,))
        p.start()
        processes.append(p)
    consumers_string = os.getenv(consumers_key)
    consumers = consumers_string.split(";") if consumers_string else []
    for c in consumers:
        consumer, t = c.split(":")
        c_topics = t.split(",")
        for c_t in c_topics:
            p = Process(target=start_consumer, args=(c_t, consumer))
            p.start()
            processes.append(p)
    return processes


def main():
    try:
        runners = start()
        for p in runners:
            p.join()
    except Exception as e:
        if runners:
            for p in runners:
                p.terminate()
        print(f"exception: {str(e)}")

if __name__ == "__main__":
    main()
