import asyncio
import json
import os
import threading
from nonebot import get_driver, on_keyword
from nonebot.adapters.onebot.v11 import Bot, Event

from .BB_susume import BB_susume, susume_bot
from .config import Config
from .get_info import subscriptions
from .nico_auth import author_container, subscriber, subscribers_run, start_asyncio_loop
from . import get_info
from .random_cookie_image import Cookie_image_getter
from .usage import load_subscriptions
from .utils import get_chat_id


from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="n站信息发送-cookie",
    description="发送n站剧场和静画信息，默认发送cookie tag下的内容",
    usage="""指令列表（需要管理员权限）
<>为必填参数（可填多个）--为选填参数（不必写--）
last <user_uid> --fast	获取作者的最新投稿，选--fast不发送封面
sub <user_uid>	订阅作者
desub <user_uid>	取消订阅
list	列出当前订阅
关键字列表（任何人都可以使用）
随机剧场  随机发送剧场信息
随机饼图	随机发送一张饼图
订阅tag <n站tag> <生成的对应关键字>		订阅n站tag，订阅后发送关键字即可随机发送图片
删除<n站tag>	删除订阅的tag，需要先订阅才能起效""",
    config=Config,
)


global_config = get_driver().config
config = Config.parse_obj(global_config)


async def run_subscribe_update():
    await subscribers_run(get_info.subscriptions)


def start_asyncio_loop_init(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


new_loop = asyncio.new_event_loop()
threading.Thread(target=start_asyncio_loop_init, args=(new_loop,)).start()


def init_cookie_image_getter():
    global a
    a = Cookie_image_getter()
    new_loop.call_soon_threadsafe(asyncio.create_task, a.initial())


init_thread = threading.Thread(target=init_cookie_image_getter)
init_thread.start()

video_getter_json_name = "video_getter.json"
if os.path.exists(video_getter_json_name):
    with open(video_getter_json_name, 'r') as f:
        video_getter_data = json.load(f)
    video_getter = susume_bot.json_to_class(video_getter_data)
else:
    video_getter = susume_bot()

random_cookie_video = on_keyword({"随机剧场", "random video"}, block=True, priority=9)


@random_cookie_video.handle()
async def r_c_v(bot: Bot, event: Event):
    global video_getter
    asyncio.create_task(video_getter.send_random_video_to_bot(bot, event))


random_cookie_send = on_keyword({"随机饼图", "random cookie"}, block=True, priority=10)


@random_cookie_send.handle()
async def r_c_s(bot: Bot, event: Event):
    if not init_thread.is_alive():
        try:
            asyncio.create_task(a.send_random_cookie(bot, event))
        except PermissionError or ValueError:
            await bot.send(event, "操作频繁，请稍后重试")
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


stop_update = on_keyword({"停止订阅更新"}, block=True)


@stop_update.handle()
async def update_stop(bot: Bot, event: Event):
    chat_id = get_chat_id(event)
    if chat_id in subscriptions:
        subscriptions[chat_id].out_of_bot()
        await bot.send(event, "订阅更新已关闭")
    else:
        await bot.send(event, "还没有订阅任何作者")


sub_cookie_tag = on_keyword({"订阅tag"}, block=False, priority=6)


@sub_cookie_tag.handle()
async def sub_tag(bot: Bot, event: Event):
    args = str(event.get_message()).split(' ')
    try:
        tag = args[1]
        keyword_ = args[2]
        print(tag, keyword_)
    except IndexError:
        await bot.send(event, "参数错误")
        return
    try:
        b = Cookie_image_getter(tag=tag, max_page=10)
        new_loop.call_soon_threadsafe(asyncio.create_task, b.initial())
    except Exception:
        await bot.send(event, "tag无效")
        return

    async def send_cookie_twice(bot, event):
        try:
            await b.send_random_cookie(bot, event)
        except Exception:
            try:
                await b.send_random_cookie(bot, event)
            except Exception:
                await bot.send(event, "请稍后再试")

    chat_id = get_chat_id(event)
    b_activate = on_keyword({keyword_}, block=True, priority=7)

    @b_activate.handle()
    async def b_func(key_not: Bot, key_event: Event):
        chat_id_ = get_chat_id(key_event)
        if key_not == bot and chat_id_ == chat_id:
            print(keyword_, "启动")
            asyncio.create_task(send_cookie_twice(bot, event))

    b_del = on_keyword({"删除" + keyword_, "删除" + tag}, block=True, priority=2)

    @b_del.handle()
    async def def_b():
        print("")
        del b
        await bot.send(event, "已删除订阅")

    await asyncio.sleep(2)

    if not b.random_cookie_list:
        await bot.send(event, "tag无效")
        return

    await bot.send(event, "订阅成功")


use_inof = """指令列表（需要管理员权限）
<>为必填参数（可填多个）--为选填参数（不必写--）
last <user_uid> --fast	获取作者的最新投稿，选--fast不发送封面
sub <user_uid>	订阅作者
desub <user_uid>	取消订阅
list	列出当前订阅
关键字列表（任何人都可以使用）
随机饼图	随机发送一张饼图
订阅tag <n站tag> <生成的对应关键字>		订阅n站tag，订阅后发送关键字即可随机发送图片
删除<n站tag>	删除订阅的tag，需要先订阅才能起效"""

how_to_use = on_keyword({"bot用法", "机器人用法"}, block=False, priority=5)


@how_to_use.handle()
async def use_to_how(bot: Bot, event: Event):
    print("机器人用法")
    await bot.send(event, use_inof)
