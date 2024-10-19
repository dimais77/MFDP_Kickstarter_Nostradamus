import pika
import json
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")

RABBITMQ_USER='rmuser'
RABBITMQ_PASS='rmpassword'

connection_params = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=5672,
    virtual_host='/',
    credentials=pika.PlainCredentials(
        username=RABBITMQ_USER,
        password=RABBITMQ_PASS,
    ),
    heartbeat=30,
    blocked_connection_timeout=2
)


def publish_message(data, queue):
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    body = json.dumps(data)
    channel.basic_publish(exchange='', routing_key=queue, body=body)
    connection.close()
