import asyncio
import os
import random

from aiohttp import ClientSession
from nonebot.adapters.onebot.v11 import Bot, Event
import aiohttp
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from lxml import etree
try:
    from nicoinfo.plugins.nicoinfo.usage import send_image_from_ab_path
    from nicoinfo.plugins.nicoinfo.wraps import retry_async
except ValueError:
    from wraps import retry_async

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'Cookie': 'nicosid=1633700428.452220814; _ts_yjad=1633700428228; _ss_pp_id=9b353ec49aa360431471646182137066; _cc_id=f58d08fa37a8aaae434b30e83797ecfd; lang=ja-jp; area=JP; _ga_8W314HNSE8=GS1.1.1653933007.94.1.1653934013.0; _gcl_au=1.1.553504617.1659349543; pbjs_sharedId=59bf20ff-a27d-4f03-804f-b7920a216078; _fbp=fb.1.1665462893682.174282674; __gads=ID=2d7a6b88f86b06c7:T=1633700444:S=ALNI_MZV9KgdWjSDI3uzQgPo9m7Ep8C-UA; _td=ceef4192-d12e-43ba-b7c5-ed24cc177792; common-header-oshirase-open-date=2022-10-25T13:04:19.965Z; __gpi=UID=00000450e6f57b88:T=1649410308:RT=1666703067:S=ALNI_MYaaH1zOxhAP4tI_sasBqNVtWHvpQ; nico_gc=tg_s%3Df%26tg_o%3Dd; cto_bundle=0-T18V94MmR6am1ZWmVJOWt4YmY1NE5MYW5FTEtsOVRrJTJGMEklMkIwY3lPbnlSZnJsbjlWTWFDdWFweEdLeFlDT25BWXo1U29nbVNWTHRSamZKOXNRdjElMkJDcUVTZE1uVU1PVmxzSFhZT1RUTW9vcHo0UHUzdFR6YlBjQ29rNFA3Vm9BZDBCVmI5c3IwZXNIZUFLdWttVEF3MXVReXclM0QlM0Q; optimizelyEndUserId=oeu1666928747475r0.3711834985684135; _gid=GA1.2.1402785906.1667051185; _ga_7W6WKHGQTW=GS1.1.1667051183.4.1.1667051767.58.0.0; _ga_G7379W9VJ0=GS1.1.1667051183.4.1.1667051767.60.0.0; _gat_UA-88451119-5=1; _gat_NicoGoogleTagManager=1; mfa_session=87722391_m8gVOCWbbtAtvvswitvaVU2KIKiJueXI; _ga=GA1.1.747558350.1633700427; user_session=user_session_87722391_f3b01de072c501c84b48f8005b2a74be53bde8445d11f1469bfd8f6bf548eb62; user_session_secure=ODc3MjIzOTE6TTVKNll2ajhCZC5TVTVROU1UaHhKMnFRNXV6dWFWeW9vZXZ4SUUxNDVaVA; _ga_5LM4HED1NJ=GS1.1.1667051185.267.1.1667051825.1.0.0'
}

@retry_async(retries=3, delay=1)
async def get_im_date_info(id):
    url = f'http://seiga.nicovideo.jp/api/illust/info?id={id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_text = await response.text()
            soup = BeautifulSoup(response_text, 'lxml')
            date = soup.find("created").text
    return date


def to_year_and_month(date):
    date_object = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    # 从datetime对象获取年份和月份
    year = date_object.year
    month = date_object.month

    return year, month

def get_point_of_cookie(view, comment, clip, time):
    pass


def get_cookie_elements(tag: str, sort: str = "clip_created"):
    page = random.randint(1, 30)
    url = f"https://seiga.nicovideo.jp/tag/{tag}?sort={sort}&page={page}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        root = etree.HTML(response.content)
        # 使用 XPath 选择元素
        im_list = []
        elements = root.xpath('//li[@class="list_item list_no_trim2"]/a')
        for element in elements:
            im_hao = element.attrib['href'].split('/')[-1]
            im_list.append(im_hao)
        return im_list


async def download_image(url, local_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                directory = os.path.dirname(local_path)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                with open(local_path, 'wb') as file:
                    file.write(await response.read())
            else:
                return False

def get_image_url(base_url, file_id, possible_extensions):
    for ext in possible_extensions:
        url = f"{base_url}{file_id}.{ext}"
        response = requests.get(url)
        if response.status_code == 200 and 'image' in response.headers['Content-Type']:
            return url
    return None


async def get_url_im_download(im):
    id = im.split("im")[1]
    url = f"https://seiga.nicovideo.jp/image/source/{id}"
    async with ClientSession() as session:
        async with session.get(url, headers=header) as response:
            text = await response.text()
    soup = BeautifulSoup(text, "html.parser")
    div = soup.find("div", {"class": "illust_view_big"})
    data_src = div.get("data-src")
    return data_src

async def download_with_im(im, local_path="image\\"):
    print("下载", im)
    data_src = await get_url_im_download(im)
    path = os.path.abspath(f'{local_path}{im}')
    await download_image(data_src, path)



async def generate_cookie_image_url(im: str):
    id = im.split('im')[1]
    date = await get_im_date_info(id)
    year, month = to_year_and_month(date)
    url = f"https://cdn.jsdelivr.net/gh/DirtyCookies/CookieImages@main/{year}/{month}/{im}"
    return url


async def download_with_im_(im, local_path="image\\"):
    print("下载", im)
    url = await generate_cookie_image_url(im)
    png = ['png', 'jpeg', 'gif']
    tasks = [asyncio.create_task(
        download_image(url + "." + ext, os.path.abspath(f'{local_path}{im}.{ext}')))
        for ext in png]
    completed = False
    while not completed:
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            result = task.result()
            if result is not False:
                completed = True
                for pending_task in pending:
                    pending_task.cancel()
                return
        tasks = pending


async def download_muti_im(im_list: list, local="image\\"):
    print("多下载")
    tasks = [asyncio.create_task(
        download_with_im(im, local)
    ) for im in im_list]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
    return done
async def download_muti_im_(im_list: list, local="image\\"):
    print("多下载")
    tasks = [asyncio.create_task(
        download_with_im_(im, local)
    ) for im in im_list]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
    return done


class Cookie_image_getter:
    def __init__(self, tag="クッキー☆"):
        self.tag = tag
        self.random_cookie_list = []
        self.completed = []

    async def initial(self):
        self.check_usable()
        print("初始化")
        while True:
            try:
                self.random_cookie_list = get_cookie_elements(self.tag)
                await self.pick_some_cookies_to_download(4)
                break
            except Exception:
                print("网络错误，3s后进行重试")
                import time
                await asyncio.sleep(3)

            pending = asyncio.all_tasks()
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.gather(*pending))

        print("初始化完毕")

    def check_usable(self):
        if self.random_cookie_list is []:
            raise IndexError

    async def pick_some_cookies_to_download(self, some=5):
        selected_elements = random.sample(self.random_cookie_list, some)
        self.random_cookie_list = [elem for elem in self.random_cookie_list if elem not in selected_elements]
        try:
            await download_muti_im(selected_elements)
        except Exception:
            await download_muti_im_(selected_elements)
        self.completed += selected_elements

    async def send_random_cookie(self, bot: Bot, event: Event):
        print("随机饼图，启动")
        if not self.completed:
            await bot.send(event, "初始化中，请稍后再试")
            return
        # print(self.completed)
        elem = random.sample(self.completed, 1)[0]
        image_path = os.path.abspath('image')
        file_path = f'{image_path}/{elem}'
        await send_image_from_ab_path(bot, event, file_path)
        try:
            self.completed.remove(elem)
            os.remove(file_path)
        except PermissionError or ValueError:
            pass
        asyncio.create_task(self.pick_some_cookies_to_download(1))
        self.check_reload()

    def check_reload(self):
        if len(self.random_cookie_list) < 10:
            self.random_cookie_list += get_cookie_elements(self.tag)
            self.pick_some_cookies_to_download(2)


if __name__ == '__main__':
    b = Cookie_image_getter()
    asyncio.run(b.initial())
    pass

