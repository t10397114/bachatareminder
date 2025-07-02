from telegram.ext import (
    ApplicationBuilder,
)

from config import BOT_TOKEN

app = ApplicationBuilder().token(BOT_TOKEN).build()
