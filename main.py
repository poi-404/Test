import asyncio

import httpx

from app.services.llmapi.bailian_client import Qwen3LLMClient


# Initialize the client
async def main():
    http_client = httpx.AsyncClient()
    client = Qwen3LLMClient(http_client)
    stream = False
    summary_response = await client.chat(model_name="", prompt="你是谁", stream=stream)
    if stream:
        async for msg in summary_response:
            print(msg)
    else:
        print(summary_response)

asyncio.run(main())        啊实打实
