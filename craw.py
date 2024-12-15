import json
import os
import random
import shutil
import time
import requests
import logging
import threading
from io import BytesIO
from PIL import Image
from PIL.Image import UnidentifiedImageError
from requests.exceptions import *
from comicBookData import comicBookData
from comicPack import ComicPack
from bookSource import bookSource
from bs4 import BeautifulSoup

from decoder_manhua55 import decoder_manhua55

URL_HEADERS = {'User-Agent': 'Mozilla/5.0'}

logging.basicConfig(
    format='%(asctime)10s %(filename)10s#L%(lineno)4d %(levelname)5s: %(message)s',
    datefmt='%y%m%d %H:%M:%S',
    level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreadWithReturnValue(threading.Thread):
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, timeout=None):
        super().join()
        return self._return


class Craw:
    def __init__(self):
        self.comicData = comicBookData()
        self.bookSource = bookSource()
        self.comicPack = ComicPack()
        self.coverurl = None
        self.cookiles = None
        self.book_save_path = None
        self.title = None
        self.config_carw_json_find = False
        self.ok_chapter = []
        self.err_chapter = []
        self.pack_chapter = []

        # 本书目录
        self.book_path = ''

    def load_book_source(self, text):
        self.bookSource.set_pic_source(text)
        pass

    def fetch(self, url_path):
        url = self.bookSource.get_source_url()
        if url.find('http') == -1:
            url = f'https://{url}'
        url = f"{url}/{url_path}"
        req = requests.get(url, headers=URL_HEADERS)
        if req.status_code == 200:
            self.cookiles = req.cookies
            return req.text
        else:
            return None

    def set_book_save_path(self, path):
        self.book_save_path = path

    # 获取标题页
    def get_title(self):
        title_url = self.title
        text = self.fetch(title_url)
        self.bookSource.set_title(text)

    def set_title(self, title: str):
        self.title = title

    def get_config_craw_json(self, json_path):
        logging.debug(f"配置文件获取 {json_path}")
        f = open(json_path, 'r', encoding='utf-8')
        js_str = f.read()
        f.close()
        root_js = json.loads(js_str)
        if 'ok_chapter' in root_js.keys():
            self.ok_chapter = root_js['ok_chapter']
        else:
            self.ok_chapter = []
        if 'err_chapter' in root_js.keys():
            self.err_chapter = root_js['err_chapter']
        else:
            self.err_chapter = []
        if 'pack_chapter' in root_js.keys():
            self.pack_chapter = root_js['pack_chapter']
        else:
            self.pack_chapter = []

    def save_config_craw_json(self, json_path):
        root_js = {
            "ok_chapter": self.ok_chapter,
            "err_chapter": self.err_chapter,
            "pack_chapter": self.pack_chapter
        }
        js_str = json.dumps(root_js, ensure_ascii=False)
        logging.debug(f"配置文件保存 {json_path}")
        f = open(json_path, 'w', encoding='utf-8')
        f.write(js_str)
        f.close()

    # 获取书籍信息
    def get_book_param(self):
        self.comicData.book_name = self.bookSource.get_bookname()
        logging.info(f'书名 : {self.comicData.book_name}')
        self.comicData.autchor = self.bookSource.get_author()
        logging.info(f'作者 : {self.comicData.autchor}')
        self.comicData.kind = self.bookSource.get_kind()
        logging.info(f'分类 : {self.comicData.kind}')
        self.comicData.lntroiduce = self.bookSource.get_lntroiduce()
        logging.info(f'简介 : {self.comicData.lntroiduce}')
        self.coverurl = self.bookSource.get_coverurl()
        logging.info(f'封面 : {self.coverurl}')
        self.comicData.chapterlist = self.bookSource.get_chapterlist()
        logging.info(f'章节 : 数量 {len(self.comicData.chapterlist)}')


    def get_cover_pic(self, path):
        url = self.coverurl
        cover_path = f'{path}/cover.jpg'
        if os.path.isfile(cover_path):
            logging.info('封面已经获取')
            return
        headers = URL_HEADERS
        headers.update(Referer=self.bookSource.get_source_url())
        req = requests.get(url, headers=headers)
        if req.status_code != 200:
            logging.warning('获取封面数据失败')
        else:
            logging.info('获取封面数据成功')
            img = Image.open(BytesIO(req.content))
            img.save(cover_path)

    # 生成漫画文件
    def create_comicinfo(self):
        pass
    # 章节打包
    def chapter_pack(self, book_path:str, chapter:dict):
        #
        pass
    # 获取章节数据
    def get_chapter_pic(self, n_index: int, book_path: str, chapter: dict) -> dict:
        craw_all_fail_true = True
        chapter_path = f"{book_path}/{n_index + 1}-{chapter['name']}"
        logging.debug(f'处理 {n_index + 1} 章 {chapter_path}')
        if not os.path.exists(chapter_path):
            os.mkdir(f'{chapter_path}')
        # 获取网页数据
        charter_url = f"{self.bookSource.get_source_url()}{chapter['href']}"
        logging.debug(charter_url)
        headers = URL_HEADERS
        headers.update(Referer=self.bookSource.get_source_url())
        req = None
        for try_i in range(3):
            try:
                req = requests.get(charter_url, headers=headers)
            except SSLError as e:
                logging.warning(f'SSLError: 重试1次 {e}')
                continue
            except ConnectionError as e:
                logging.warning(f'ConnectionError: 重试1次 {e}')
                continue
            break
        if None == req:
            craw_all_fail_true = False
        elif req.status_code == 200:
            # logging.debug(f"req {req.content}")
            soup = BeautifulSoup(req.content, 'html.parser')
            # print(soup.find_all('script'))
            param = ''
            for scr_noe in soup.find_all('script'):
                if scr_noe.text.find('param') != -1:
                    param = scr_noe.text
                    break
            param = param.split('params')[1].split("'")[1]
            logging.debug(f'{n_index + 1} 获取到加密数据 ')
            # logging.debug(f'param {param}')
            decoder = decoder_manhua55()
            json_str = decoder.decryptParams(s_prarm=param)
            # print(json_str)
            js = json.loads(json_str)
            n_pic_index = 0
            image_list = js['images']
            logging.debug(f'检测 第 {n_index + 1} 章一共 {len(image_list)} 张图')

            for _ in image_list:
                n_pic_index += 1
                image_path = f'{chapter_path}/image{n_pic_index}.jpeg'
                url = ''
                # 图位置
                print("\r", end="")
                p_x = int(n_pic_index / len(image_list) * 100)
                print("第{}章 进度: {}%: ".format(n_index + 1, p_x), "▓" * (p_x // 2), end="")
                # 检测到重复文件时跳过
                if os.path.isfile(image_path):
                    continue
                for try_i in range(3):
                    try:
                        url_list = ['https://img1-2.baipiaoguai.org',
                                    'https://img1-3.baipiaoguai.org',
                                    'https://img1-4.baipiaoguai.org']
                        rade = int(random.uniform(0, len(url_list) - 1))
                        url = f'{url_list[rade]}' + _
                        headers = URL_HEADERS
                        headers.update(Referer=self.bookSource.get_source_url())
                        req = requests.get(url, headers=headers)
                    except SSLError as e:
                        logging.warning(f'SSLError: 重试1次 {e}')
                        continue
                    except ConnectionError as e:
                        logging.warning(f'ConnectionError: 重试1次 {e}')
                        continue
                    break

                if req.status_code == 200:
                    logging.debug(f"已获取图片 {n_pic_index}")
                    try:
                        img = Image.open(BytesIO(req.content)).convert("RGB")
                        img.save(image_path, 'jpeg', quality=80, compress_level=5)
                    except UnidentifiedImageError as e:
                        logging.error(f"UnidentifiedImageError 图片导入 err {charter_url} url {url} {e}")
                        craw_all_fail_true = False
                        pass
                else:
                    craw_all_fail_true = False

        if craw_all_fail_true:
            logging.info(f"本章完成 {chapter_path}")
        else:
            logging.warning(f"本章还有异常需要处理 {chapter_path}")
        return {"index": n_index, "craw_ok_flag": craw_all_fail_true}

    def save_pack(self, index):
        chapter_name = f"{index + 1}-{self.comicData.chapterlist[index]['name']}"
        logging.debug(f"打包章节 {chapter_name}")
        self.comicPack.save_comic_info(f"{self.book_path}/{chapter_name}", self.comicData, chapter_name)
        self.comicPack.comic_chapter_pack(f"{self.book_path}/{chapter_name}", self.book_path, chapter_name)

    def rm_chapter(self, index):
        chapter_name = f"{index + 1}-{self.comicData.chapterlist[index]['name']}"
        shutil.rmtree(f"{self.book_path}/{chapter_name}")

    def get_is_pack(self, index):
        chapter_name = f"{index + 1}-{self.comicData.chapterlist[index]['name']}"
        return os.path.isfile(f"{self.book_path}/{chapter_name}.cbz")

    # craw 处理流程
    #  获取漫画各项参数，获取配置文件， 异常的或者新增的抓取， 抓取完成后，进行 打包处理 保存配置文件
    def craw(self):
        self.get_title()
        self.get_book_param()


        if self.book_save_path != None:
            if not os.path.exists(self.book_save_path):
                os.mkdir(self.book_save_path)
            book_path = f"{self.book_save_path}/{self.comicData.book_name}"
        else:
            book_path = f"./{self.comicData.book_name}"
        config_json_path = f"{book_path}/carw_config.json"
        # 新建文件夹
        if not os.path.exists(book_path):
            os.mkdir(f"{book_path}")
            logging.debug(f"新建文件夹 {book_path}")
            # 新建 配置 json文件
        else:
            logging.debug('已检测到有文件夹存在')
        self.book_path = book_path
        js_str = '{}'
        if os.path.isfile(config_json_path):
            self.config_carw_json_find = True
            self.get_config_craw_json(config_json_path)
        else:
            self.config_carw_json_find = False
            # 没找到配置文件，默认配置

        # 获取封面
        self.get_cover_pic(book_path)

        # 获取章节
        n_chapter_num = len(self.comicData.chapterlist)
        thread_num = 50
        thread_index = 0
        threads = []
        chapter_index = 0
        logging.info(f"开始处理章节")
        while True:
            # 生产者
            if len(threads) < thread_num:
                if chapter_index < n_chapter_num:
                    index = chapter_index
                    chapternone = self.comicData.chapterlist[index]
                    chapter_cbz = f"{index+1}-{chapternone['name']}"
                    chapter_name = f"{index}${chapternone['name']}"
                    if (self.config_carw_json_find == False
                            or not (chapter_name in self.ok_chapter)):
                        # 搜索 无配置文件 以及 报错的 章节重新处理
                        if not self.get_is_pack(index):
                            thread = ThreadWithReturnValue(target=self.get_chapter_pic,
                                                           args=(index, book_path, self.comicData.chapterlist[index]))
                            threads.append(thread)
                            thread.start()
                    else:
                        if self.get_is_pack(index):
                            logging.debug(f"该章节已处理,跳过 {index+1}-{chapternone['name']}")
                        else:
                            self.save_pack(index)
                            self.rm_chapter(index)

                    chapter_index += 1

            # 消费者
            for _ in threads:
                if not _.is_alive():
                    # 完成处理后调用完成后处理函数
                    req = _.join()
                    index = req['index']
                    chapter_name = f"{index}${self.comicData.chapterlist[index]['name']}"
                    if not req['craw_ok_flag']:
                        if not chapter_name in self.err_chapter:
                            self.err_chapter.append(chapter_name)
                    else:
                        self.save_pack(index)
                        self.rm_chapter(index)

                    threads.remove(_)
            if len(threads) == 0 and chapter_index == n_chapter_num:
                # 处理完了
                break
            time.sleep(0.05)

        # 完成处理后保存文件
        self.save_config_craw_json(config_json_path)


if __name__ == '__main__':
    data = comicBookData()
    data.url_title = 'manhua417361'
    f = open('./bookSource/manhua55.json', 'r+', encoding='utf-8')
    comic_list = [
        'manhua417361',  # 我为邪帝
        # 'manhua417363',  # 元尊
        'manhua419046',  # 斗破
        'manhua419028',  # 斗罗大陆4终极斗罗
        'manhua419021',  # 妖神记
    ]
    # 加载 书源
    craw = Craw()
    craw.load_book_source(f.read())
    craw.set_book_save_path('./comic')

    for _ in comic_list:
        # 加载
        craw.set_title(_)
        # 开始爬数据
        craw.craw()
