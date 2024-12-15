import logging

from comicBookData import comicBookData
import zipfile
import os
from jinja2 import Environment

class ComicPack:

    def __init__(self):
        self.writer = "-"
        self.title = '-'
        # 作者
        self.writer = '-'
        # 出版社
        self.publisher = "-"
        self.genre = "-"
        # 简介
        self.summary = '-'
        self.language = "zh"
        self.pages = "-"
        self.year = "-"
        self.month = '-'
        self.day = '-'
        self.pack_pach = '-'
        pass

    def set_pack_path(self, path):
        self.pack_pach = path


    # 漫画文件夹打包
    def comic_chapter_pack(self, src_pach, dest_path, pack_name):
        if not os.path.isdir(src_pach):
            logging.error(f"源文件目录异常 {src_pach}")
            return False
        if not os.path.isdir(dest_path):
            logging.error(f"目标文件目录异常 {dest_path}")
            return False
        # 创建打包环境
        cbz = zipfile.ZipFile(f"{dest_path}/{pack_name}.cbz", 'w', allowZip64=True)
        image_list = os.listdir(src_pach)
        for _ in image_list:
            file = f"{src_pach}/{_}"
            # logging.debug(f"get {file}")
            if os.path.isfile(file):
                f = open(file, 'rb')
                data = f.read()
                cbz.writestr(_, data)
                f.close()
        cbz.close()
        pass

    # 漫画 info 信息保存
    def save_comic_info(self, dest_path, comicinfo:comicBookData, chapter_name):
        self.writer = comicinfo.autchor
        self.title = comicinfo.book_name
        self.summary = comicinfo.lntroiduce
        listdir = os.listdir(dest_path)
        image_count = 0
        for _ in listdir:
            file = f"{dest_path}/{_}"
            if os.path.isfile(file) and _.find("image") != -1:
                image_count += 1

        with open(os.path.join(os.path.dirname(__file__), './ComicInfo.xml'), 'r',
                  encoding='utf-8') as f:
            template = f.read()
        comicinfo = Environment().from_string(template).render(
            series=self.title,
            title=chapter_name,
            writer=self.writer,
            publisher=self.publisher,
            genre=self.genre,
            summary=self.summary,
            language=self.language,
            pages=image_count,
        )
        f = open(f'{dest_path}/ComicInfo.xml', 'w', encoding="utf-8")
        f.write(str(comicinfo))
        f.close()

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)10s %(filename)10s#L%(lineno)4d %(levelname)5s: %(message)s',
        datefmt='%y%m%d %H:%M:%S',
        level=logging.INFO)
    pack = ComicPack()
    pack.set_pack_path("./comic")
    pack.save_comic_info()
    pack.comic_chapter_pack("./comic/我为邪帝/1-预告", "./comic", "1-预告")
    pass