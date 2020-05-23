# -*- coding: utf-8 -*-
# by nan gong er gou
import json
import os

import requests
from bs4 import BeautifulSoup as bs

import functions
from album import Album


class Zhubo:
    def __init__(self, zhubo_url, zhubo_id, header=None):
        self.zhubo_url = zhubo_url
        self.zhubo_id = zhubo_id
        self.header = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
        } if header == None else header
        self.album_list = []
        self.time_api = 'https://www.ximalaya.com/revision/time'
        self.album_list_api = 'https://www.ximalaya.com/revision/user/pub?page=%d&pageSize=%d&keyWord=&uid=%d&orderType=2'
        self.session = requests.session()

    def get_album_list(self):
        # 获取主播的主页
        main_page = self.session.get(self.zhubo_url, headers=self.header)
        # print(main_page.text)
        main_page = bs(main_page.text)
        # has_more = main_page.find(class_='fr pointer-orange text-mid gray-9 _Wq')
        # has_more = main_page.find(class_='text-xxl fl text-no-bold _Wq')
        has_more = main_page.find(class_='anchor-detail-content-block-header o-hidden _Wq').find(class_='fr '
                                                                                                        'pointer-orange text-mid gray-9 _Wq')
        # print(has_more)
        if has_more == None:  # 所有的专辑在主页都显示了
            album_list = main_page.find(class_='anchor-detail-content-block-list _Wq')
            album_list = album_list.find_all(class_='anchor-detail-album-item mgb-10 mgr-20 _Wq')
            for item in album_list:
                album_info = item.find(class_='album-wrapper sm _Ht').find(class_='album-title line-2 sm _Ht')
                # print(album_info.prettify())
                # print('专辑标题：%s' % album_info['title'])
                # print('专辑链接：%s' % album_info['href'])
                self.album_list.append({'title': album_info['title'], 'href': album_info['href']})
            # print(self.album_list)
        else:  # 主播的专辑数量过多，无法全部展示在主页，所有要进入专门的专辑列表页进行抓取
            # print(has_more.prettify())
            album_list_url = has_more['href']
            # print(album_list_url)
            self.header['xm-sign'] = functions.get_xml_sign(session=self.session, time_api=self.time_api,
                                                            header=self.header)
            page, pageSize = 1, 10
            album_list_api = self.album_list_api % (page, pageSize, self.zhubo_id)
            album_list_response = self.session.get(album_list_api,
                                                   headers=self.header)
            album_list_response = json.loads(album_list_response.text)
            album_list = album_list_response['data']['albumList']
            while len(album_list) > 0:
                # print(page)
                # print(album_list)
                self.album_list.extend(album_list)
                page += 1
                album_list_api = self.album_list_api % (page, pageSize, self.zhubo_id)
                album_list_response = self.session.get(album_list_api,
                                                       headers=self.header)
                album_list_response = json.loads(album_list_response.text)
                album_list = album_list_response['data']['albumList']
            # print(len(self.album_list))

    def get_zhubo_albums(self, save_path=None):
        self.get_album_list()
        if save_path is None:
            save_path = '%d' % self.zhubo_id
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        for album in my_zhubo.album_list[:3]:
            # print(album)
            album_url = 'https://www.ximalaya.com%s' % album['albumUrl']
            print(album_url)
            album_id = album['id']
            my_album = Album(album_url=album_url, album_id=album_id)
            my_album.get_album(save_path='%s/%d' % (save_path, album_id))


if __name__ == '__main__':
    # 测试下载指定主播
    # zhubo_url = 'https://www.ximalaya.com/zhubo/71860763' # 这个主播只有两个专辑，在主页上已经完全显示出来了
    zhubo_url = 'https://www.ximalaya.com/zhubo/4228109'
    zhubo_id = int(zhubo_url.split('/')[-1])
    save_path = '%d' % zhubo_id
    my_zhubo = Zhubo(zhubo_url, zhubo_id)
    my_zhubo.get_zhubo_albums(save_path=save_path)
