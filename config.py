import logging
import os

from pytz import timezone

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

SCHEDULE_BEFORE_HOUR = os.getenv("SCHEDULE_BEFORE_HOUR")
SCHEDULE_BEFORE_MINUTE = os.getenv("SCHEDULE_BEFORE_MINUTE")
SCHEDULE_SAME_HOUR = os.getenv("SCHEDULE_SAME_HOUR")
SCHEDULE_SAME_MINUTE = os.getenv("SCHEDULE_SAME_MINUTE")

TIMEZONE = timezone("Asia/Novosibirsk")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

GROUPS = [
    {
        "name": "Бачата, начинашки",
        "days": ["Monday", "Friday"],
        "time": {"Monday": "10:00", "Friday": "09:00"},
        "chat_id": os.getenv("CHAT_ID_BACHATA"),
        "ask_day": "before",  # спрашиваем за день до
    },
    {
        "name": "Бачата продолжающ. группа",
        "days": ["Monday", "Friday"],
        "time": {"Monday": "11:00", "Friday": "10:00"},
        "chat_id": os.getenv("CHAT_ID_BACHATA_ADV"),
        "ask_day": "before",  # спрашиваем за день до
    },
    {
        "name": "Solo latina",
        "days": ["Monday", "Thursday"],
        "time": {"Monday": "09:00", "Thursday": "12:00"},
        "chat_id": os.getenv("CHAT_ID_SOLO_LATINA"),
        "ask_day": "before",  # спрашиваем за день до
    },
    {
        "name": "Малыши 3-5 лет",
        "days": ["Tuesday", "Thursday"],
        "time": {"Tuesday": "19:00", "Thursday": "19:00"},
        "chat_id": os.getenv("CHAT_ID_KIDS_3_5"),
        "ask_day": "same",  # спрашиваем в тот же день
    },
    {
        "name": "Малыши 5-6 лет",
        "days": ["Monday", "Thursday"],
        "time": {"Monday": "17:00", "Thursday": "17:00"},
        "chat_id": os.getenv("CHAT_ID_KIDS_5_6"),
        "ask_day": "same",  # спрашиваем в тот же день
    },
    {
        "name": "Пары 7-13 лет",
        "days": ["Monday", "Thursday"],
        "time": {"Monday": "19:00", "Thursday": "18:00"},
        "chat_id": os.getenv("CHAT_ID_MIAMI_PAIRS"),
        "ask_day": "same",  # спрашиваем в тот же день
    },
    # для тестирования
    # {
    #     "name": "Test before",
    #     "days": ["Tuesday", "Friday"],
    #     "time": {"Tuesday": "10:00", "Friday": "09:00"},
    #     "chat_id": "-1002837893273",
    #     "ask_day": "before",  # спрашиваем за день до
    # },
    # {
    #     "name": "Test same",
    #     "days": ["Monday", "Friday"],
    #     "time": {"Monday": "10:00", "Friday": "09:00"},
    #     "chat_id": "-1002837893273",
    #     "ask_day": "same",  # спрашиваем за день до
    # },
]
