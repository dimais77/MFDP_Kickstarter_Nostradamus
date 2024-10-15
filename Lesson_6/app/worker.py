import os
import pika
import json
import pandas as pd
from database.database import get_session
from models.mltask import MLTask
from services.crud import mltask as MLTaskService
from services.crud import mlmodel as MLModelService
from publisher import publish_message
import logging
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)


def predict_callback(ch, method, properties, body):
    logging.debug(f"Received message: {body}")
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    if "task_id" not in data:
        logging.error("Received data without 'task_id'")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    task_id = data["task_id"]
    session = get_session()
    mltask = MLTaskService.get_task_by_id(task_id, session)

    if not mltask:
        logging.error(f"Task {task_id} not found")
        session.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    model = MLModelService.get_model_by_id(mltask.model_id, session)
    if not model:
        logging.error(f"Model {mltask.model_id} not found")
        MLTaskService.update_task_status(mltask, 'failed', session)
        session.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    input_data = data.get("input_data")
    if input_data is None:
        logging.error(f"Input data missing for task {task_id}")
        MLTaskService.update_task_status(mltask, 'failed', session)
        session.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    input_df = pd.DataFrame([input_data])

    try:
        prediction = model.predict(input_df)
        predicted_quality = int(prediction[0])

        mltask.output_data = json.dumps(
            {"predicted_quality": predicted_quality})
        MLTaskService.update_task_status(mltask, 'completed', session)

        prediction_history_data = {
            "task_id": mltask.task_id,
            "model_id": mltask.model_id,
            "input_data": mltask.input_data,
            "output_data": mltask.output_data
        }
        publish_message(prediction_history_data, queue='prediction_history')

    except Exception as e:
        logging.error(f"Error processing task {task_id}: {str(e)}")
        MLTaskService.update_task_status(mltask, 'failed', session)
    finally:
        session.close()

    ch.basic_ack(delivery_tag=method.delivery_tag)


def save_prediction_callback(ch, method, properties, body):
    logging.debug(f"Received message: {body}")
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    if "task_id" not in data:
        logging.error("Received data without 'task_id'")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    task_id = data["task_id"]
    session = get_session()
    mltask = next(
        session.query(MLTask).filter(MLTask.id == task_id).limit(1).all(),
        None)

    if not mltask:
        logging.error(f"Task {task_id} not found")
        session.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    logging.info(f"Saving prediction history for task {task_id}")
    session.close()
    ch.basic_ack(delivery_tag=method.delivery_tag)


RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT = 5672
RABBITMQ_USER = os.getenv('RABBITMQ_USER')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')


def start_worker():
    connection_params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host='/',
        credentials=pika.PlainCredentials(
            username=RABBITMQ_USER,
            password=RABBITMQ_PASSWORD,
        ),
        heartbeat=30,
        blocked_connection_timeout=2
    )

    connection = pika.BlockingConnection(connection_params)

    channel = connection.channel()
    channel.queue_declare(queue='ml_tasks')
    channel.queue_declare(queue='prediction_history')

    channel.basic_consume(queue='ml_tasks',
                          on_message_callback=predict_callback)
    channel.basic_consume(queue='prediction_history',
                          on_message_callback=save_prediction_callback)

    logging.info(' [*] Waiting for messages. To exit press CTRL+C')
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    start_worker()
