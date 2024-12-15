

class comicBookData:
    def __init__(self):
        # 作者
        self.autchor = ''
        # 书名
        self.book_name = ''
        #
        self.kind = ''
        # 简介
        self.lntroiduce = None
        # list [dict{name:章节名称 href:地址 chapter:}]
        self.chapterlist = None
