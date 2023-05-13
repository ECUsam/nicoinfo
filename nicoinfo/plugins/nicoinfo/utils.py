from datetime import datetime, timedelta
from nonebot.adapters.onebot.v11 import Event

def get_chat_id(event: Event):
    return str(event.get_user_id()) if event.is_tome() else str(event.group_id)

async def time_detect(input_time_str):
    input_time = datetime.strptime(input_time_str, "%Y年%m月%d日 %H：%M：%S")
    now = datetime.now()
    time_difference = now - input_time
    if time_difference < timedelta(minutes=1):
        return True
    else:
        return False