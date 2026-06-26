"""LLM-driven E2E check for the cat's MCP server (ROADMAP Phase 5 verify).

A free Gemini model connects to the running cat over MCP and is told, in plain
English, to save and list a workspace. We hand Gemini the cat's tool schemas,
run whatever calls it asks for against the live MCP session, and feed the
results back — proving an external LLM client can drive the workspace ops.

Dev-only, not part of the app. Run the cat first (`python main.py`), then:

    pip install google-genai          # not in requirements.txt on purpose
    GEMINI_API_KEY=... python e2e_llm.py

ponytail: explicit call loop, not genai's tools=[session] auto-mode — that path
deep-copies the live session (asyncio Futures) and dies on `cannot pickle
Future` in google-genai 2.10. MCP inputSchema is already JSON Schema, so the
loop is a few lines: declare tools, run the calls it asks for, send results back.
"""
import asyncio
import os

from google import genai
from google.genai import types
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "http://localhost:8765/mcp"
PROMPT = "Save my current workspace as 'work', then list my saved workspaces."


async def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            decls = [types.FunctionDeclaration(
                name=t.name, description=t.description,
                parameters_json_schema=t.inputSchema) for t in tools]
            config = types.GenerateContentConfig(tools=[types.Tool(function_declarations=decls)])

            contents = [types.Content(role="user", parts=[types.Part(text=PROMPT)])]
            while True:
                resp = await client.aio.models.generate_content(
                    model="gemini-2.5-flash", contents=contents, config=config)
                calls = resp.function_calls
                if not calls:
                    print(resp.text)
                    return
                contents.append(resp.candidates[0].content)
                for c in calls:
                    out = await session.call_tool(c.name, dict(c.args))
                    text = out.content[0].text if out.content else ""
                    print(f"  -> {c.name}({dict(c.args)}) = {text}")
                    contents.append(types.Content(role="user", parts=[types.Part(
                        function_response=types.FunctionResponse(name=c.name, response={"result": text}))]))


if __name__ == "__main__":
    asyncio.run(main())
