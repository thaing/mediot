import json
from kafka import KafkaProducer
from kafka.errors import KafkaError


class KafkaException(Exception):
    pass


class KafkaProducerService:
    def __init__(self, broker: str):
        self.broker = broker
        self._producer: KafkaProducer | None = None

    def connect(self):
        self._producer = KafkaProducer(
            bootstrap_servers=self.broker,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            max_block_ms=5000,
            api_version_auto_timeout_ms=5000,
        )

    def publish(self, topic: str, key: str | None, value: dict):
        if self._producer is None:
            raise KafkaException("Producer not connected")
        try:
            future = self._producer.send(topic, key=key, value=value)
            result = future.get(timeout=10)
            return result
        except KafkaError as e:
            raise KafkaException(f"Failed to publish to {topic}: {e}") from e

    def close(self):
        if self._producer is not None:
            self._producer.flush()
            self._producer.close()
            self._producer = None


producer_service: KafkaProducerService | None = None


def get_producer() -> KafkaProducerService:
    global producer_service
    if producer_service is None:
        from src.app.config import settings

        producer_service = KafkaProducerService(settings.KAFKA_BROKER)
    return producer_service
