import json
import asyncio
import logging
from services.queue_service import redis_client, QUEUE_NAME, publish_event
from src.workflow import workflow_builder
from src.pdf_generator import generate_pdf

logger = logging.getLogger(__name__)
orchestrator_worker = workflow_builder()


async def process_jobs():
    """Continuously listens to queue and processes report and pdf jobs"""
    logger.info("Worker started, listening for jobs...")

    while True:
        try:
            job_data = await redis_client.brpop(QUEUE_NAME, timeout=1)

            if not job_data:
                continue

            _, raw = job_data
            job = json.loads(raw)
            job_id = job["job_id"]
            topic = job["topic"]
            job_type = job.get("job_type", "report")  # default to report

            logger.info(f"Processing {job_type} job {job_id} for topic: {topic}")

            await publish_event(job_id, {
                "status": "processing",
                "message": f"{job_type.upper()} generation started"
            })

            # Run workflow for both types — both need the report first
            result = await orchestrator_worker.ainvoke({"topic": topic})
            report = result.get("final_report", "")

            if job_type == "report":
                await publish_event(job_id, {
                    "status": "completed",
                    "report": report
                })

            elif job_type == "pdf":
                pdf_path = await generate_pdf(report)
                await publish_event(job_id, {
                    "status": "completed",
                    "pdf_path": pdf_path,       # worker saves file, sends path
                    "message": f"PDF ready. Download at /download-pdf/{pdf_path}"
                })

            logger.info(f"Job {job_id} completed")

        except Exception as e:
            logger.error(f"Worker error: {e}")
            await publish_event(job_id, {
                "status": "failed",
                "message": f"Job failed: {str(e)}"
            })
            await asyncio.sleep(1)