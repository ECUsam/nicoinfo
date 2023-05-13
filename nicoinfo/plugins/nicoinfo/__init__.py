import asyncio
import threading
from nonebot import get_driver, on_keyword
from nonebot.adapters.onebot.v11 import Bot, Event
from .config import Config
from .get_info import subscriptions
from .nico_auth import author_container, subscriber, subscribers_run, start_asyncio_loop
from . import get_info
from .random_cookie_image import Cookie_image_getter
from .utils import get_chat_id

global_config = get_driver().config
config = Config.parse_obj(global_config)


async def run_subscribe_update():
    await subscribers_run(get_info.subscriptions)


def init_cookie_image_getter():
    global a
    a = Cookie_image_getter()


new_loop = asyncio.new_event_loop()
threading.Thread(target=start_asyncio_loop, args=(new_loop, run_subscribe_update())).start()

init_thread = threading.Thread(target=init_cookie_image_getter)
init_thread.start()

random_cookie_send = on_keyword({"随机饼图", "random cookie"}, block=True)


@random_cookie_send.handle()
async def r_c_s(bot: Bot, event: Event):
    if not init_thread.is_alive():
        await a.send_random_cookie(bot, event)
    else:
        await bot.send(event, "初始化未完成，请等待片刻")


start_update = on_keyword({"启动订阅更新", "启动订阅"}, block=True)
@start_update.handle()
async def update_start(bot: Bot, event: Event):
    chat_id = get_chat_id(event)
    if chat_id in subscriptions:
        subscriptions[chat_id].get_the_bot(bot)
        await bot.send(event, "订阅更新已开启")
    else:
        await bot.send(event, "还没有订阅任何作者")


stop_update = on_keyword({"停止订阅更新"}, block= True)
@stop_update.handle()
async def update_stop(bot: Bot, event: Event):
    chat_id = get_chat_id(event)
    if chat_id in subscriptions:
        subscriptions[chat_id].out_of_bot()
        await bot.send(event, "订阅更新已关闭")
    else:
        await bot.send(event, "还没有订阅任何作者")
