# Kafka and Zookeeper
FROM python:3-alpine

RUN apk add --update openjdk8-jre supervisor bash gcompat

ENV ZOOKEEPER_VERSION 3.4.13
ENV ZOOKEEPER_HOME /opt/zookeeper-"$ZOOKEEPER_VERSION"

RUN wget -q http://archive.apache.org/dist/zookeeper/zookeeper-"$ZOOKEEPER_VERSION"/zookeeper-"$ZOOKEEPER_VERSION".tar.gz -O /tmp/zookeeper-"$ZOOKEEPER_VERSION".tgz
RUN ls -l /tmp/zookeeper-"$ZOOKEEPER_VERSION".tgz
RUN tar xfz /tmp/zookeeper-"$ZOOKEEPER_VERSION".tgz -C /opt && rm /tmp/zookeeper-"$ZOOKEEPER_VERSION".tgz
ADD assets/conf/zoo.cfg $ZOOKEEPER_HOME/conf

ENV SCALA_VERSION 2.13
ENV KAFKA_VERSION 2.6.0
ENV KAFKA_HOME /opt/kafka_"$SCALA_VERSION"-"$KAFKA_VERSION"
ENV KAFKA_DOWNLOAD_URL https://archive.apache.org/dist/kafka/"$KAFKA_VERSION"/kafka_"$SCALA_VERSION"-"$KAFKA_VERSION".tgz
ENV MOCK_CONSUMERS consumer1:topic1;consumer2:topic2,topic1,topic3;consumer3:topic4
ENV MOCK_PRODUCERS producer1:topic1,topic3;producer2:topic2,topic4

RUN wget -q $KAFKA_DOWNLOAD_URL -O /tmp/kafka_"$SCALA_VERSION"-"$KAFKA_VERSION".tgz
RUN tar xfz /tmp/kafka_"$SCALA_VERSION"-"$KAFKA_VERSION".tgz -C /opt && rm /tmp/kafka_"$SCALA_VERSION"-"$KAFKA_VERSION".tgz
RUN pip install kafka-python

ADD assets/scripts/start-kafka.sh /usr/bin/start-kafka.sh
ADD assets/scripts/start-zookeeper.sh /usr/bin/start-zookeeper.sh
ADD assets/scripts/mocks.py /usr/bin/mocks.py

# Supervisor config
ADD assets/supervisor/kafka.ini assets/supervisor/zookeeper.ini assets/supervisor/mocks.ini /etc/supervisor.d/

# 2181 is zookeeper, 9092 is kafka
EXPOSE 2181 9092

CMD ["supervisord", "-n"]
