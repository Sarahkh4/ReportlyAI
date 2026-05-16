from fastapi import APIRouter
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse
from services.queue_service import redis_client
import json
import asyncio

router = APIRouter()


async def stream_events(job_id: str):
    """Reusable event streaming logic for any job ID"""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(job_id)

    try:
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=30
            )
            if message:
                data = json.loads(message["data"])
                yield {"data": json.dumps(data)}

                if data["status"] in ("completed", "failed"):
                    break

            await asyncio.sleep(0.1)
    finally:
        await pubsub.unsubscribe(job_id)


@router.get("/status/{job_id}")
async def report_status(job_id: str):
    """SSE endpoint for report jobs"""
    return EventSourceResponse(stream_events(job_id))


@router.get("/pdf-status/{job_id}")
async def pdf_status(job_id: str):
    """SSE endpoint for PDF jobs"""
    return EventSourceResponse(stream_events(job_id))


@router.get("/download-pdf/{file_name}")
async def download_pdf(file_name: str):
    """Serve the generated PDF file once ready"""
    return FileResponse(file_name, filename="report.pdf", media_type="application/pdf")