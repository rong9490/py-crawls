#! /usr/bin/env python3
# encoding: utf-8

"""
@site: http://www.dytt8.net/html/gndy/dyzz/list_23_1.html
@description: 爬电影天堂[lxml + xpath + requests]
"""

import time
from typing import Dict, List, TypedDict, NotRequired

BASE_URL = 'http://www.dytt8.org/'
HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36',
}

def main_url_2_detail_urls(index: int, url: str):
    """
    处理一页数据: 一个具体url及其详情
    :param url:
    :return:
    """
    print('{} :: {}'.format(index, url))
    pass

def spider_main_flow():
    """
    核心爬虫流程的入口
    :return:
    """
    base_url: str = 'http://www.dytt8.net/html/gndy/dyzz/list_23_{}.html'

    for index in range(1, 11):
        print('开始爬取第{}页'.format(index))
        # 每页的url(电影列表)
        url = base_url.format(index)
        main_url_2_detail_urls(index, url)

        time.sleep(2)

    pass

if __name__ == '__main__':
    spider_main_flow()
    pass