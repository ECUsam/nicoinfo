import json
from typing import Union
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, Message
import aiohttp
from lxml import etree
import os
import nonebot.log as logging

from nicoinfo.plugins.nicoinfo.nico_auth import subscriber
from nicoinfo.plugins.nicoinfo.utils import get_chat_id

logger = logging.logger


def video_info_to_str(last: dict):
    return f"""视频标题: {last['title']}
作者：{last['auth']}
视频日期: {last['date_info']}
sm号:{last['sm']}
视频链接: {last['url']}
视频简介： {last['description']}"""


async def download_image(url, local_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                directory = os.path.dirname(local_path)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                with open(local_path, 'wb') as file:
                    file.write(await response.read())


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html_content = await response.text()
                return html_content
            else:
                print(f"Error: {response.status}")
                return None


async def extract_og_image(url):
    html_content = await fetch(url)
    sm = url.split('/')[-1]
    if html_content:
        parser = etree.HTMLParser(encoding='utf-8')
        tree = etree.fromstring(html_content, parser)
        OGimage = tree.xpath('//meta[@property="og:image"]/@content')
        if OGimage:
            await download_image(str(OGimage[0]), f'./image/{sm}.png')
            return f'./image/{sm}.png'


def subscriptions_to_json_data(subscriptions: dict[str, subscriber]) -> dict:
    json_data_of_subscriptions = {}
    for chat_id in subscriptions:
        json_data_of_subscriptions[chat_id] = subscriptions[chat_id].get_json_data()
    return json_data_of_subscriptions


def json_data_to_subscriptions(json_data):
    subscriptions = {}
    for chat_id in json_data:
        subscriptions[chat_id] = subscriber.create_from_json_data(json_data[chat_id])
    return subscriptions


def load_subscriptions(filename):
    try:
        with open(filename, "r") as file:
            subscriptions = json.load(file)
    except FileNotFoundError:
        subscriptions = {}
    subscriptions = json_data_to_subscriptions(subscriptions)
    return subscriptions


def save_subscriptions(subscriptions, filename):
    subscriptions_data = subscriptions_to_json_data(subscriptions)
    with open(filename, "w") as file:
        json.dump(subscriptions_data, file)


# TODO：可能写错了
async def send_image_and_text(bot: Bot, event: Event, text: str, image: str):
    text = MessageSegment.text(text)
    local_image_path = image
    ab_local_image_path = os.path.abspath(local_image_path)
    local_image = MessageSegment.image(f"file:///{ab_local_image_path}")
    message = Message(text + local_image)
    await bot.send(event, message)


async def send_image_from_ab_path(bot: Bot, event: Event, path: str):
    image = MessageSegment.image(f"file:///{path}")
    await bot.send(event, image)


async def send_image_from_url(bot: Bot, event: Event, url: str):
    base_name = url.split('/')[-1]
    local_image_path = f"image/{base_name}"
    ab_local_image_path = os.path.abspath(local_image_path)
    await download_image(url, ab_local_image_path)
    local_image = MessageSegment.image(f"file:///{ab_local_image_path}")
    await bot.send(event, local_image)
    os.remove(ab_local_image_path)


async def get_samune_from_video(video: Union[dict, str]) -> str:
    if isinstance(video, dict):
        video = video['url']
    logger.debug("video信息：")
    logger.debug(video)
    return await extract_og_image(video)


# TODO:私人群聊，发图不发图，event
async def last_video_send_message(bot: Bot, send_image: bool, last_video: dict, event: Event | str | int,
                                  is_private: bool):
    if type(event) == Event:
        event = get_chat_id(event)
    text = video_info_to_str(last_video)
    if is_private:
        if not send_image:
            logger.info(text)
            await bot.send_private_msg(user_id=event, message=Message(text))
            return
        video = await get_samune_from_video(last_video)
        logger.debug("封面信息" + str(video))
        await send_image_and_text(bot, event, text, str(video))
        os.remove(video)


async def send_last_video_to_private_or_group(bot: Bot, event_id, last_video: dict, is_private: bool):
    text = video_info_to_str(last_video)
    local_image_path = await get_samune_from_video(last_video)
    ab_local_image_path = os.path.abspath(local_image_path)
    local_image = MessageSegment.image(f"file:///{ab_local_image_path}")
    message = Message(text + local_image)
    if is_private:
        await bot.send_private_msg(user_id=event_id, message=message)
    else:
        await bot.send_group_msg(group_id=event_id, message=message)


async def send_last_video_to_private_or_group_fast(bot: Bot, event_id, last_video: dict, is_private: bool):
    text = video_info_to_str(last_video)
    if is_private:
        await bot.send_private_msg(user_id=event_id, message=text)
    else:
        await bot.send_group_msg(group_id=event_id, message=text)
