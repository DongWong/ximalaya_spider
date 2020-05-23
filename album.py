# -*- coding: utf-8 -*-
# by nan gong er gou
import json
import os
import time
import requests
from bs4 import BeautifulSoup as bs
import functions


class Album:
    def __init__(self, album_url, album_id, header=None):
        self.album_url = album_url
        self.album_id = album_id
        self.album_api = 'https://www.ximalaya.com/revision/play/album?albumId=%d&pageNum=%d&sort=0&pageSize=30'
        # self.album_api = 'https://www.ximalaya.com/revision/play/v1/show?id=291938702&sort=0&size=30&ptype=1'
        self.time_api = 'https://www.ximalaya.com/revision/time'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
        } if header == None else header
        self.s = requests.session()
        self.album_title = ''
        self.max_page = 1

    def download_audio(self, audio_title, audio_src, save_path):
        while save_path.endswith('/'):
            save_path = save_path[:-1]
        # 请求源地址的链接，得到response
        r_audio_src = self.s.get(audio_src, headers=self.header)
        # 构造保存路径
        m4a_path = '%s/%s.m4a' % (save_path, audio_title)
        if not os.path.exists(m4a_path):
            with open(m4a_path, 'wb') as f:
                # 写入
                f.write(r_audio_src.content)
                print('%s\t保存完毕...' % m4a_path)
        else:
            print('%s\t已存在' % m4a_path)

    def get_album(self, save_path, album_url=None, album_id=None):
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        album_url = self.album_url if album_url is None else album_url
        album_id = self.album_id if album_id is None else album_id
        # 根据有声书ID构造url
        album_html = self.s.get(album_url, headers=self.header)
        # outf = open('html.txt','w')
        # outf.write(album_html.text)
        # outf.close()
        album_html = bs(album_html.text, 'html.parser')
        # print(album_html.prettify())
        title = album_html.find(class_='title lO_')
        self.album_title = title.string
        print('专辑名称为：', self.album_title)

        max_page = album_html.find('input', class_='control-input _Xo')
        if max_page == None:
            self.max_page = 1
        else:
            self.max_page = int(max_page['max'])
        print('专辑最大页数为：', self.max_page)
        for page in range(1, self.max_page + 1):
            print('第%d页' % page)
            # 获取当前时间对应的 xm-sign 添加到请求头中
            self.header['xm-sign'] = functions.get_xml_sign(session=self.s, time_api=self.time_api, header=self.header)
            # 访问链接
            r = self.s.get(self.album_api % (album_id, page), headers=self.header)  # 返回的是一个字典
            print(self.album_api % (album_id, page))
            r_json = json.loads(r.text)
            for audio in r_json['data']['tracksAudioPlay']:
                # print(audio)
                # exit()
                # 获取json中的每个音频的标题以及播放源地址
                audio_title = str(audio['trackName']).replace(' ', '')
                audio_src = audio['src']
                if audio['isPaid']:
                    print('音频 %s 需要付费' % audio_title)
                if audio_src is None:
                    print('音频 %s 缺少下载地址信息' % audio_title)
                    continue
                print('音频标题：%s\n音频地址：%s' % (audio_title, audio_src))
                # 交给下载的方法
                self.download_audio(audio_title, audio_src, save_path)
            # 每爬取1页，30个音频，休眠3秒
            time.sleep(3)


if __name__ == '__main__':
    # 测试下载指定的专辑
    album_url = 'https://www.ximalaya.com/keji/36283567/'
    album_id = 36283567
    save_path = '36283567'
    my_album = Album(album_url=album_url, album_id=album_id)
    my_album.get_album(save_path=save_path)
