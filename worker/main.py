import logging
import os
import signal
import sys
import time

from src.db.session import SessionLocal

from worker.consumer import create_consumer, consume
from worker.processor import process_reading

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")
TOPIC = "device-readings"
GROUP_ID = "medIoT-worker"

running = True


def shutdown(signum, frame):
    global running
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    running = False


def main():
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    consumer = create_consumer(BROKER, GROUP_ID, TOPIC)
    logger.info(f"Worker started, listening to {TOPIC} on {BROKER}")

    processed = 0
    errors = 0
    start_time = time.time()

    try:
        for key, value in consume(consumer):
            if not running:
                break

            db = SessionLocal()
            try:
                if process_reading(db, value):
                    processed += 1
                    consumer.commit()
                else:
                    errors += 1
            finally:
                db.close()

            if processed % 100 == 0 and processed > 0:
                elapsed = int(time.time() - start_time)
                logger.info(
                    f"Stats: {processed} processed, {errors} errors, "
                    f"{elapsed}s uptime"
                )
    finally:
        logger.info(
            f"Shutting down. Final stats: {processed} processed, "
            f"{errors} errors"
        )
        consumer.close()


if __name__ == "__main__":
    main()
