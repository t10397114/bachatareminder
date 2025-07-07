import asyncio
from datetime import datetime, timedelta

from config import (
    GROUPS,
    SCHEDULE_BEFORE_HOUR,
    SCHEDULE_BEFORE_MINUTE,
    SCHEDULE_SAME_HOUR,
    SCHEDULE_SAME_MINUTE,
    TIMEZONE,
)
from tg_service import ask_admin


async def scheduler():
    print("[scheduler] запустился")
    already_asked = set()

    while True:
        try:
            now = datetime.now(TIMEZONE)
            print(f"[scheduler] now = {now}")

            # Проверка для "before" групп — в 13:00, спрашиваем про завтра
            minutes = SCHEDULE_BEFORE_MINUTE
            if now.hour == SCHEDULE_BEFORE_HOUR and minutes <= now.minute <= minutes + 4 and "before" not in already_asked:
                target_day = now + timedelta(days=1)
                weekday = target_day.strftime("%A")
                print(f"[scheduler] Проверяем группы на завтра ({weekday})")

                for group in GROUPS:
                    if group.get("ask_day") == "before" and weekday in group["days"]:
                        class_time = group["time"][weekday]
                        await ask_admin(group, class_time)

                already_asked.add("before")
                print("[scheduler] Спросили 'before' группы")

            minutes = SCHEDULE_SAME_MINUTE
            # Проверка для "same" групп — в 11:00, спрашиваем про сегодня
            if now.hour == SCHEDULE_SAME_HOUR and minutes <= now.minute <= minutes + 4 and "same" not in already_asked:
                weekday = now.strftime("%A")
                print(f"[scheduler] Проверяем группы на сегодня ({weekday})")

                for group in GROUPS:
                    if group.get("ask_day") == "same" and weekday in group["days"]:
                        class_time = group["time"][weekday]
                        await ask_admin(group, class_time)

                already_asked.add("same")
                print("[scheduler] Спросили 'same' группы")

            # Сброс флага на следующий день
            if now.hour == 0 and now.minute < 5:
                already_asked.clear()
                print("[scheduler] Обнуление already_asked для нового дня")

            await asyncio.sleep(20)
        except Exception as e:
            print(f"Ошибка в scheduler {e}")
            await asyncio.sleep(10)
