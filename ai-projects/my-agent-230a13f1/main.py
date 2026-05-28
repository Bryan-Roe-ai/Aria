# Copyright (c) Microsoft. All rights reserved.

"""Streaming echo agent using azure-ai-agentserver-responses.

Echoes user input back as a streamed response via Server-Sent Events (SSE).
Each word is sent as a separate delta event to demonstrate real-time streaming.

Usage::

    # Start the agent
    python main.py

    # Send a streaming request
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "echo", "input": "Hello world!", "stream": true}'

    # Send a non-streaming request (also works, returns JSON)
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "echo", "input": "Hello world!"}'
"""

import asyncio

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
)

ECHO_PREFIX = "🔊 Echo: "

app = ResponsesAgentServerHost()


@app.response_handler
async def echo_streaming_handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Echo user input back as a streamed response, word by word.

    ``TextResponse`` handles the full SSE lifecycle automatically:
    ``response.created`` → ``response.in_progress`` → message/content
    events → ``response.completed``.  Passing an async iterable to
    ``text=`` streams each chunk as a separate ``output_text.delta`` event.
    """

    async def generate_words():
        user_input = await context.get_input_text() or "Hello! Send me a message and I'll echo it back."
        echo_text = f"{ECHO_PREFIX}{user_input}"
        words = echo_text.split()
        for i, word in enumerate(words):
            await asyncio.sleep(0.1)  # simulate token-by-token latency
            yield word if i == 0 else f" {word}"

    return TextResponse(context, request, text=generate_words())


if __name__ == "__main__":
    app.run()
