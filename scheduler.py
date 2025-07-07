from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import (
    GROUPS,
    SCHEDULE_BEFORE_HOUR,
    SCHEDULE_BEFORE_MINUTE,
    SCHEDULE_SAME_HOUR,
    SCHEDULE_SAME_MINUTE,
    TIMEZONE,
    logger,
)
from tg_service import ask_admin

scheduler = AsyncIOScheduler(timezone="Asia/Novosibirsk")

async def ask_before_groups():
    now = datetime.now(TIMEZONE)
    target_day = now + timedelta(days=1)
    weekday = target_day.strftime("%A")
    logger.info(f"[ask_before_groups] Проверяем группы на завтра ({weekday})")

    for group in GROUPS:
        if group.get("ask_day") == "before" and weekday in group["days"]:
            class_time = group["time"][weekday]
            await ask_admin(group, class_time)

async def ask_same_day_groups():
    now = datetime.now(TIMEZONE)
    weekday = now.strftime("%A")
    logger.info(f"[ask_same_day_groups] Проверяем группы на сегодня ({weekday})")

    for group in GROUPS:
        if group.get("ask_day") == "same" and weekday in group["days"]:
            class_time = group["time"][weekday]
            await ask_admin(group, class_time)


async def setup_scheduler():
    scheduler.add_job(
        func=ask_before_groups,
        trigger=CronTrigger(hour=SCHEDULE_BEFORE_HOUR, minute=SCHEDULE_BEFORE_MINUTE, timezone=TIMEZONE),
        name="Ask before groups",
        replace_existing=True,
    )
    scheduler.add_job(
        func=ask_same_day_groups,
        trigger=CronTrigger(hour=SCHEDULE_SAME_HOUR, minute=SCHEDULE_SAME_MINUTE, timezone=TIMEZONE),
        name="ask_same_day_groups",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("[scheduler] Started with APScheduler")
