import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def send_notification(self, transaction_id: int) -> None:
    """Dispatch a notification for the given transaction.

    Body is intentionally a no-op until a real notification channel is wired
    in. We log so we can observe the call surface in dev environments.
    """
    logger.info("Notification dispatched for transaction %s", transaction_id)
