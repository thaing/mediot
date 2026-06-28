import json
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


def create_consumer(broker: str, group_id: str, topic: str) -> KafkaConsumer:
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=broker,
        group_id=group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
    )
    return consumer


def consume(consumer: KafkaConsumer):
    for message in consumer:
        try:
            yield (message.key, message.value)
        except Exception as e:
            logger.warning(f"Skipping malformed message: {e}")
            continue
