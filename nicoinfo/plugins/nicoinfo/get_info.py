import requests
from nonebot.params import CommandArg
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, Message
from .nico_auth import auth_auth_info, subscriber
from .usage import load_subscriptions, save_subscriptions, send_image_and_text, get_samune_from_video, \
    send_image_from_url
from .usage import logger, video_info_to_str
import os

from .utils import get_chat_id

subscriptions_filename = "subscriptions.json"
if os.path.exists(subscriptions_filename):
    subscriptions = load_subscriptions(subscriptions_filename)
else:
    subscriptions = {}


async def get_subscriber(event: Event) -> subscriber:
    logger.info("用户ID:" + str(event.get_user_id()))
    logger.info("is_tome:" + str(event.is_tome()))
    chat_id = get_chat_id(event)
    logger.info("chat_id:" + chat_id)
    if chat_id not in subscriptions:
        # 如果字典中没有该群聊或私人会话的订阅器实例，创建一个并添加到字典中
        is_private = event.is_tome()
        subscriptions[chat_id] = subscriber(chat_id, is_private)

    return subscriptions[chat_id]


sub_cmd = on_command("sub", aliases={"订阅"}, block=True)


@sub_cmd.handle()
async def sub_command(bot: Bot, event: Event):
    args = str(event.get_message()).split(' ')[1]
    try:
        uid = int(args)
    except Exception:
        await bot.send(event, Message("参数错误"))
        return
    subscriber_instance = await get_subscriber(event)
    subscriber_instance.sub(uid)
    await bot.send(event, Message("订阅成功"))
    logger.info(subscriptions)
    save_subscriptions(subscriptions, subscriptions_filename)
    logger.info("参数：" + args)
    if "last" or "need last" in args:
        a = auth_auth_info(str(uid))
        last = a.get_last_video()
        await auth_last_video.finish(video_info_to_str(last))


desub_cmd = on_command("desub", aliases={"取消订阅", "cancel subscribe", "del"}, block=True, priority=5)
@desub_cmd.handle()
async def desub_command(bot: Bot, event: Event):
    del_list = []
    chat_id = get_chat_id(event)
    args = str(event.get_message()).split(' ')
    logger.debug(args)
    for arg in args:
        if arg.isdigit():
            if subscriptions[chat_id].if_suber(arg):
                subscriptions[chat_id].desub(arg)
                del_list.append(arg)
    if del_list:
        del_info = ",".join(del_list)
        await bot.send(event, "已删除订阅" + del_info)
        save_subscriptions(subscriptions, subscriptions_filename)
    else:
        await bot.send(event, "订阅号错误")


# 其他命令和方法也可以使用 get_subscriber 函数来获取相应的订阅器实例
get_list = on_command("list", aliases={"sub_list", "订阅列表"}, block=True)


@get_list.handle()
async def get_list(bot: Bot, event: Event):
    args = str(event.get_message()).strip()
    message = ""
    subscriber_instance = await get_subscriber(event)
    subscribers_list = subscriber_instance.get_sub_list()
    for suber in subscribers_list:
        message += (str(suber) + ':' + subscribers_list[suber]['auth'] + '\n')

    await bot.send(event, Message("当前订阅列表：\n" + message))


auth_last_video = on_command("last", aliases={"最后投稿", "last video", "最新"}, priority=5)


@auth_last_video.handle()
async def last_video(bot: Bot, event: Event, args: Message = CommandArg()):
    if not args:
        await auth_last_video.finish("需要作者uid")
    args = str(args).split(' ')
    fast_run = ("fast" or "快速" or "无封面" or "fast run") in args
    logger.info('快速启动:' + str(fast_run))
    for arg in args:
        logger.info(arg)
        if str(arg).isdigit():
            a = auth_auth_info(arg)
            try:
                last = a.get_last_video()
            except requests.exceptions.ConnectTimeout:
                await bot.send(event, Message("链接失败，请稍后重试"))
                break
            text = video_info_to_str(last)
            if fast_run:
                logger.info(text)
                await bot.send(event, Message(text))
                continue
            video = await get_samune_from_video(last)
            logger.debug("封面信息" + str(video))
            await send_image_and_text(bot, event, text, str(video))
            os.remove(video)


send_img = on_command("img", aliases={'image'})


@send_img.handle()
async def send_img_(bot: Bot, event: Event, args: Message = CommandArg()):
    for arg in args:
        await send_image_from_url(bot, event, str(arg))


