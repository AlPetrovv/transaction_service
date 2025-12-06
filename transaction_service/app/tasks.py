import logging
import random
import time

from transaction_service.celery import app

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_notification(self):
    try:
        raise_error = random.choice([True, False])
        if raise_error:
            logger.error("send_notification error", exc_info=True)
            raise ValueError("Something went wrong")
        time.sleep(5)
        logger.info("Notification sent")
    except Exception as exc:
        raise self.retry(exc=exc)




