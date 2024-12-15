import os
from bs4 import BeautifulSoup
import logging
import json

class bookSource:
    def __init__(self):
        self.title_soup = None
        self.json = None
        pass
    def set_pic_source(self, source):
        self.json = json.loads(source)
        logging.debug(f'pic source json: {self.json}')

    def set_title(self, title_content):
        self.title_soup = BeautifulSoup(title_content, 'html.parser')

    def get_meta(self, soup:BeautifulSoup, name):
        tags = soup.find_all('meta')
        for tag in tags:
            if tag.get('name') == name:
                return tag.get('content')

    def get_title_param(self, json_name, is_list=False):
        if self.title_soup == None or self.json == None or json_name == '':
            logging.warn('param not set')
            return None
        rule = self.json[json_name]
        # rule 规则处理
        # meta 规则， meta. 后接key_name
        # id规则，匹配 后缀 div内部数据
        if rule != '':
            index = rule.find('.')
            rule_i = rule[0:index]
            rule_last = rule[index+1:]
            logging.debug(f'rule: {rule_i} {rule_last}')
            tags = None
            if rule_i == 'meta':
                return self.get_meta(self.title_soup, rule_last)
            if rule_i == 'p':
                tags = self.title_soup.find_all('p')
                for tag in tags:
                    for t in tag.get('class'):
                        if t.find('a') != -1:
                            txt = tag.contents[0]
                            return txt

            if rule_i == 'id':
                p_index = rule_last.find('.')
                a_index = rule_last.find('@')
                if(a_index != -1 or p_index != -1):
                    logging.debug(f'rule: {a_index} {p_index}')
                    if a_index < p_index:
                        rule_tag = rule_last[0:a_index]
                        rule_last = rule_last[a_index+1:]
                        logging.debug(f'rule_tag: {rule_tag}')
                        tags = self.title_soup.find_all(name='div', attrs={'id':rule_tag})[0]
                        # logging.debug(tags)
                        rule_i = rule_last.find('tag')
                        if rule_i != -1:
                            rule_tag = rule_last[0:rule_i]
                            rule_last = rule_last[rule_i:]
                            if rule_last.find('a') != -1:
                                none = tags.find_all(name='a')
                                index = 1
                                chapter_list = []
                                for tag in none:
                                    name = tag.find_all('span')[0].contents[0]
                                    chapter_none = {"chapter":index, "href":tag.get('href'), "name":name}
                                    index += 1
                                    chapter_list.append(chapter_none)
                                return chapter_list



    def get_source_url(self):
        if self.json == None:
            logging.error('param not set')
            return None
        return self.json['bookSourceurl']
    # 获取书名
    def get_bookname(self):
        return self.get_title_param('ruleSearchName')

    # 获取作者
    def get_author(self):
        return self.get_title_param('ruleSearchAuthor')

    # 分类规则
    def get_kind(self):
        return self.get_title_param('ruleSearchKind')
    # 简介
    def get_lntroiduce(self):
        return self.get_title_param('rulelntroduce')
    # 封面地址
    def get_coverurl(self):
        return self.get_title_param('ruleCoverUrl')

    # 获取章节列表
    def get_chapterlist(self):
        return self.get_title_param('ruleChapterList', is_list=True)
