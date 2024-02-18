import threading
import time
import requests

# 定义一个下载函数，模拟下载操作
def download(url):
    print(f"Downloading {url}")
    # 模拟下载操作，这里使用 requests 库发送一个简单的 GET 请求
    response = requests.get(url)
    print(f"Downloaded {url}")

# 创建线程类
class DownloadThread(threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url

    def run(self):
        print(time.time())
        download(self.url)

# 创建并启动两个线程，每个线程下载不同的内容
thread1 = DownloadThread("https://www.example.com/file1")
thread2 = DownloadThread("https://www.example.com/file2")

thread1.start()
thread2.start()
print(111)
# 主线程等待两个线程执行完成
thread1.join()
thread2.join()

print("All downloads are completed!")
