import asyncio
import os

from aiohttp import web
from telegram.ext import (
    CallbackQueryHandler,
)

from bot import app
from config import logger
from scheduler import setup_scheduler
from tg_service import handle_callback


async def handle_ping(_):
    return web.Response(text="I'm alive!")


async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"[webserver] Starting on port {port}")
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


def main():
    loop = asyncio.get_event_loop()
    loop.create_task(setup_scheduler())
    loop.create_task(start_webserver())

    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()

if __name__ == "__main__":
    logger.info(f"Вызов main")
    main()
