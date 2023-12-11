import asyncio
import time

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

chat_router = APIRouter(prefix="/chat", tags=["chat"])


STREAM_DELAY = 1
RETRY_TIMEOUT = 15000


def get_server_time():
    return time.ctime()


@chat_router.get("/stream")
async def event_stream(request: Request):
    async def event_generator():
        for i in range(1, 4):
            yield f"event: add\nretry: {RETRY_TIMEOUT}\ndata: {i}\nid: {i}\n\n"
            await asyncio.sleep(STREAM_DELAY)
        yield "event: finish\ndata: finish\n\n"

    headers = {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache",
    }
    return StreamingResponse(event_generator(), headers=headers)
