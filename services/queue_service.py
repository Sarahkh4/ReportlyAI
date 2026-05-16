import redis.asyncio as redis
import json
import uuid
import os

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
QUEUE_NAME = "report_jobs"


async def enqueue_job(topic: str, job_type: str = "report") -> str:
    """
    Push a new job into the Redis queue.
    job_type: 'report' for text report, 'pdf' for PDF file
    Returns a unique job ID.
    """
    job_id = uuid.uuid4().hex

    job = {
        "job_id": job_id,
        "topic": topic,
        "job_type": job_type,   # ← tells worker what to do
        "status": "pending"
    }

    await redis_client.lpush(QUEUE_NAME, json.dumps(job))
    return job_id


async def publish_event(job_id: str, data: dict):
    """Publish progress/completion event to a Redis channel"""
    await redis_client.publish(job_id, json.dumps(data))