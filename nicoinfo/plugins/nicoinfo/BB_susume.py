import asyncio
import json
import random
from datetime import datetime
import requests
from lxml import etree
import math
from nonebot.adapters.onebot.v11 import Bot, Event
import time

def get_chat_id(event: Event):
    return str(event.get_user_id()) if event.is_tome() else str(event.group_id)

try:
    from nicoinfo.plugins.nicoinfo.usage import get_samune_from_video
except ValueError:
    from usage import get_samune_from_video


def get_point_of_video(view, comment, like, mylist):
    return int(view) * 1 + int(comment) * 20 + int(like) * 20 + int(mylist) * 100


def time_difference_from_now(time_string: str) -> int:
    time_format = "%Y/%m/%d %H:%M"
    given_time = datetime.strptime(time_string, time_format)
    current_time = datetime.now()
    time_difference = current_time - given_time
    return int(time_difference.total_seconds())


def video_info_to_str(last: dict):
    return f"""视频标题: {last['title']}
视频日期: {last['date_info']}
sm号:{last['sm']}"""


class BB_susume:
    def __init__(self, tag="BBクッキー☆劇場", sort='h'):
        self.tag = tag
        self.link = "https://www.nicovideo.jp/tag/" + tag
        # self.susumeta = []  # 会话：[已推荐列表]
        self.susume_list = {}
        self.sort = sort

    def init(self):
        while len(self.susume_list) < 20:
            self.get_random_video(5)

    def get_random_video(self, num=5):
        page = random.randint(1, 200)
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(self.link + f"?page={page}&sort={self.sort}&order=d", headers=headers)
        # print(self.link + f"?page={page}&sort={self.sort}&order=d")
        if response.status_code == 200:
            root = etree.HTML(response.content)
            sm_dic = {}
            elements = root.xpath('//li[@data-video-item]')
            for element in elements:
                if 'data-id' in element.attrib:
                    sm = element.attrib['data-id']
                elif 'data-video-id':
                    sm = element.attrib['data-video-id']
                    date = element.xpath('.//span[@class="time"]/text()')[0]
                    title = element.xpath('.//a[@title]/text()')[0]
                    view = element.xpath('.//li[@class="count view"]/span/text()')[0].replace(',', '')
                    if int(view) > 300000:
                        break
                    comment = element.xpath('.//li[@class="count comment"]/span/text()')[0].replace(',', '')
                    like = element.xpath('.//li[@class="count like"]/span/text()')[0].replace(',', '')
                    mylist = element.xpath('.//li[@class="count mylist"]/span/text()')[0].replace(',', '')
                    video_length = element.xpath('.//span[@class="videoLength"]/text()')[0].replace(',', '')
                    point = get_point_of_video(view, comment, like, mylist)
                    log_time = math.log(time_difference_from_now(date), 72000000)
                    url = f"https://www.nicovideo.jp/watch/{sm}"
                    sm_dic[sm] = {'point': int(point / (log_time ** 4)), 'title': title, 'date_info': date, 'sm': sm, 'url': url, 'view': view, 'comment': comment, 'video_length': video_length}
                    # print(title, int(point / log_time))
            sorted_sm = sorted(sm_dic.keys(), key=lambda key: sm_dic[key]['point'], reverse=True)
            for i in range(num):
                self.susume_list[sorted_sm[i]] = sm_dic[sorted_sm[i]]
            # print(self.susume_list)


class susume_bot:
    def __init__(self, tag="BBクッキー☆劇場", member=0):
        self.tag = tag
        self.susume_func = BB_susume(self.tag)
        # self.sub_list = {}
        self.member = member
        self.susumeta = {} # member: [(sm, last_susume), ]
        """
        sub_list: 
            member:{
                is_private
                is_open
                susume_list
                susumeta :{sm: last_susume}
            }
        """
        self.bot = None

    def get_the_bot(self, bot):
        self.bot = bot

    def out_of_bot(self):
        self.bot = None

    async def get_random_video_info(self):
        self.susume_func.init()
        random_sm = random.choice(list(self.susume_func.susume_list.keys()))
        random_video = self.susume_func.susume_list[random_sm]
        des = video_info_to_str(random_video)
        del self.susume_func.susume_list[random_sm]
        return des, random_video

    def check_if_susumeta_in_3_day(self, sm, chat_id):
        if chat_id in self.susumeta:
            if sm in self.susumeta[chat_id]:
                old_time = self.susumeta[chat_id][sm]
                current_timestamp = time.time()
                if current_timestamp - old_time <= 1678224000:
                    return True
        return False


    async def send_random_video_to_bot(self, bot: Bot, event: Event):
        des, last = await self.get_random_video_info()
        chat_id = get_chat_id(event)
        if self.check_if_susumeta_in_3_day(last['sm'], chat_id):
            asyncio.create_task(self.send_random_video_to_bot(bot, event))
            return
        if chat_id not in self.susumeta:
            self.susumeta[chat_id] = []
        self.susumeta[chat_id].append({last['sm']: time.time()})
        from nicoinfo.plugins.nicoinfo.usage import send_last_video_to_private_or_group_BBsusume as send_message
        await send_message(bot, chat_id, last, event.is_tome())
        self.class_save_to_json()

    def class_save_to_json(self):
        json_data = {'tag': self.tag, 'susumeta': self.susumeta}
        with open('video_getter.json', 'w') as f:
            json.dump(json_data, f)

    @staticmethod
    def json_to_class(json: dict):
        subscriber_instance = susume_bot(json['tag'])
        subscriber_instance.susumeta = json['susumeta']
        return subscriber_instance


if __name__ == "__main__":
    a = susume_bot()
    asyncio.run(a.get_random_video_info())
