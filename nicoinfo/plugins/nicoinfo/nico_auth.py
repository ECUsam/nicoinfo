import asyncio
import threading
import requests
from bs4 import BeautifulSoup

try:
    from utils import time_detect
    from wraps import repeat_every_30_seconds
except ModuleNotFoundError:
    from nicoinfo.plugins.nicoinfo.utils import time_detect
    from nicoinfo.plugins.nicoinfo.wraps import repeat_every_30_seconds


class auth_auth_info:
    def __init__(self, uid: str):
        self.uid = uid
        self.api_url = f"https://www.nicovideo.jp/user/{uid}/video?rss=2.0"
        self.items, self.auth = self._get_videos_info()

    def _get_videos_info(self):
        response = requests.get(self.api_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "lxml")
        item = soup.find_all("item")
        auth = soup.select('channel dc\\:creator')
        return item, auth

    def get_last_video(self):
        item = self.items[0]
        title = item.title.text
        video_url = item.link.next_sibling.strip()
        real_url = video_url.split('?')[0]
        p_nico_description = item.find("p", class_="nico-description").text

        p_nico_info = item.find("p", class_="nico-info")
        video_id = real_url.split('/')[-1]
        # 如果找到了<p>标签，则提取日期信息
        if p_nico_info:
            date_info = p_nico_info.find("strong", class_="nico-info-date").text
        else:
            date_info = "无日期信息"

        last_video = {
            'title': title,
            'date_info': date_info,
            'url': real_url,
            'description': p_nico_description,
            'auth': self.auth[0].text,
            'sm': video_id
        }
        return last_video

    def get_videos_list(self):
        videos_list = {}
        for item in self.items:
            title = item.title.text
            video_url = item.link.next_sibling.strip()
            real_url = video_url.split('?')[0]
            p_nico_description = item.find("p", class_="nico-description").text

            p_nico_info = item.find("p", class_="nico-info")
            video_id = real_url.split('/')[-1]
            # 如果找到了<p>标签，则提取日期信息
            if p_nico_info:
                date_info = p_nico_info.find("strong", class_="nico-info-date").text
            else:
                date_info = "无日期信息"
            video = {
                'title': title,
                'date_info': date_info,
                'url': real_url,
                'description': p_nico_description,
                'auth': self.auth[0].text,
                'sm': video_id
            }
            videos_list[video_id] = video
        videos_list['auth'] = self.auth[0].text
        return videos_list


async def detect_new_video(uid):
    video = auth_auth_info(uid)
    last_video = video.get_last_video()
    if await time_detect(last_video['date_info']):
        return last_video


class author_container:
    def __init__(self):
        self.auth_list = {}

    def sub_auth(self, uid: str, need_last: bool = False):
        _ = auth_auth_info(uid)
        self.auth_list[uid] = _.get_videos_list()
        if need_last:
            return _.get_last_video()

    async def get_new_video(self):
        for auth in self.auth_list:
            await detect_new_video(auth)

    def update_list(self, data: dict):
        self.auth_list.update(data)


class subscriber:
    def __init__(self, member: str, is_private: bool = False):
        self.member = member
        self.is_private = is_private
        self.container = author_container()
        self.bot = None

    def get_the_bot(self, bot):
        self.bot = bot

    def out_of_bot(self):
        self.bot = None

    def sub(self, uid, need_last: bool = False):
        self.container.sub_auth(uid, need_last)

    def desub(self, uid):
        del self.container.auth_list[uid]

    def if_suber(self, uid):
        if uid in self.container.auth_list:
            return True
        else:
            return False

    def get_sub_list(self):
        return self.container.auth_list

    async def update_sub_list(self, suber):
        last_video = await detect_new_video(suber)
        if not last_video:
            print(suber + ":无视频更新。" + "会话：" + self.member)
            return None
        if last_video['sm'] not in self.container.auth_list[suber]:
            self.container.auth_list[suber]['sm'] = last_video
            if await time_detect(last_video['date_info']):
                print(last_video)
                return last_video

    def get_json_data(self) -> dict:
        subscriber_json = {
            "member": self.member,
            "is_private": self.is_private,
            "container": self.container.auth_list
        }
        return subscriber_json

    @staticmethod
    def create_from_json_data(json_data: dict):
        subscriber_instance = subscriber(json_data["member"], json_data["is_private"])
        subscriber_instance.container.update_list(json_data["container"])
        return subscriber_instance

    @repeat_every_30_seconds
    async def continuously_update(self, ):
        results = await asyncio.gather(*(self.update_sub_list(suber) for suber in self.container.auth_list))
        if self.bot:
            for result in results:
                if result and type(result) is dict:
                    from nicoinfo.plugins.nicoinfo.usage import send_last_video_to_private_or_group as send_message
                    await send_message(self.bot, self.member, result, self.is_private)


async def subscribers_run(subscribers: dict[str, subscriber]):
    tasks = [subscriber_instance.continuously_update() for subscriber_instance in subscribers.values()]
    await asyncio.gather(*tasks)


def start_asyncio_loop(loop, coroutine):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coroutine)


async def main():
    subscriber_instance = subscriber('test')
    subscriber_instance.sub('4970449')
    subscriber_instance.sub('51546188')
    subscriber_instance2 = subscriber('test2')
    subscriber_instance2.sub('125247562')
    subscribers = {"114514": subscriber_instance,
                   "1919810": subscriber_instance2}
    # await subscriber_instance.continuously_update()
    await subscribers_run(subscribers)


if __name__ == '__main__':
    print(111)  # 主程序可以继续执行其他操作
    new_loop = asyncio.new_event_loop()
    threading.Thread(target=start_asyncio_loop, args=(new_loop, main())).start()
    print(222)
