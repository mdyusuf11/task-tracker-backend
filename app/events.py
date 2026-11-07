import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)


def publish_task_event(event_type: str, task_id: int, payload: dict[str, Any]) -> None:
    """Publish a task lifecycle event. Uses Pub/Sub when configured; otherwise logs."""
    settings = get_settings()
    message = {
        "event_type": event_type,
        "task_id": task_id,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        **payload,
    }

    if not settings.gcp_project_id or not settings.pubsub_topic:
        logger.info("task_event(local): %s", json.dumps(message))
        return

    try:
        from google.cloud import pubsub_v1

        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(settings.gcp_project_id, settings.pubsub_topic)
        publisher.publish(topic_path, json.dumps(message).encode("utf-8"))
    except Exception:
        logger.exception("Failed to publish task event; falling back to log")
        logger.info("task_event(fallback): %s", json.dumps(message))
