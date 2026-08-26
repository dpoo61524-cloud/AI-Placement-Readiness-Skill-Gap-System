import sys
import os
import asyncio
import uvicorn

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
os.environ["PYTHONUNBUFFERED"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

from backend.main import app

async def main():
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_level="info", loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    print("Starting Uvicorn Server via asyncio.run()...", flush=True)
    asyncio.run(main())
