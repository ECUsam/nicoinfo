import requests
from bs4 import BeautifulSoup
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    'Cookie': 'nicosid=1633700428.452220814; _ts_yjad=1633700428228; _ss_pp_id=9b353ec49aa360431471646182137066; _cc_id=f58d08fa37a8aaae434b30e83797ecfd; lang=ja-jp; area=JP; _ga_8W314HNSE8=GS1.1.1653933007.94.1.1653934013.0; _gcl_au=1.1.553504617.1659349543; pbjs_sharedId=59bf20ff-a27d-4f03-804f-b7920a216078; _fbp=fb.1.1665462893682.174282674; __gads=ID=2d7a6b88f86b06c7:T=1633700444:S=ALNI_MZV9KgdWjSDI3uzQgPo9m7Ep8C-UA; _td=ceef4192-d12e-43ba-b7c5-ed24cc177792; common-header-oshirase-open-date=2022-10-25T13:04:19.965Z; __gpi=UID=00000450e6f57b88:T=1649410308:RT=1666703067:S=ALNI_MYaaH1zOxhAP4tI_sasBqNVtWHvpQ; nico_gc=tg_s%3Df%26tg_o%3Dd; cto_bundle=0-T18V94MmR6am1ZWmVJOWt4YmY1NE5MYW5FTEtsOVRrJTJGMEklMkIwY3lPbnlSZnJsbjlWTWFDdWFweEdLeFlDT25BWXo1U29nbVNWTHRSamZKOXNRdjElMkJDcUVTZE1uVU1PVmxzSFhZT1RUTW9vcHo0UHUzdFR6YlBjQ29rNFA3Vm9BZDBCVmI5c3IwZXNIZUFLdWttVEF3MXVReXclM0QlM0Q; optimizelyEndUserId=oeu1666928747475r0.3711834985684135; _gid=GA1.2.1402785906.1667051185; _ga_7W6WKHGQTW=GS1.1.1667051183.4.1.1667051767.58.0.0; _ga_G7379W9VJ0=GS1.1.1667051183.4.1.1667051767.60.0.0; _gat_UA-88451119-5=1; _gat_NicoGoogleTagManager=1; mfa_session=87722391_m8gVOCWbbtAtvvswitvaVU2KIKiJueXI; _ga=GA1.1.747558350.1633700427; user_session=user_session_87722391_6dc20b4a32e0a8614c9084dd66a698c4fb552c1b9a8fad0a79e59a2437384532; user_session_secure=ODc3MjIzOTE6a3JiSWRWNkw5bUsybml5dThwQzRsd3FIQlVqdXRnSDE4ZlV1OFZyUEI3ZQ; _ga_5LM4HED1NJ=GS1.1.1667051185.267.1.1667051825.1.0.0'
}

def get_url_im_download(im):
    id = im.split("im")[1]
    url = f"https://seiga.nicovideo.jp/image/source/{id}"
    print(url)
    text = requests.get(url, headers=header).text
    soup = BeautifulSoup(text, "html.parser")
    div = soup.find("div", {"class": "illust_view_big"})
    data_src = div.get("data-src")
    return data_src

print(get_url_im_download("im11375651"))