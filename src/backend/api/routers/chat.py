import hashlib
import os
from typing import List

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import AzureOpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

chat_router = APIRouter(prefix="/chat", tags=["chat"])


STREAM_DELAY = 1
RETRY_TIMEOUT = 15000


def calculate_md5(string):
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode("utf-8"))
    return md5_hash.hexdigest()


load_dotenv()  # take environment variables from .env.


client = AzureOpenAI(
    api_version=os.environ["OPENAI_API_VERSION"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_deployment="gpt-35-turbo",
)


def completion(
    messages: str | List[ChatCompletionMessageParam],
    temperature=0,
):
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
        temperature=temperature,
    )

    for chunk in stream:
        if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            # sys.stdout.write(content)
            yield f"event: message\ndata: {content}\nid: 1\n\n"
    yield "event: end\ndata: \nid: 1\n\n"


@chat_router.get("/stream")
async def event_stream(prompt: str):
    headers = {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache",
    }
    return StreamingResponse(completion(prompt), headers=headers)
