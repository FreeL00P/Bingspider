#coding:gbk
# @Time: 2021/12/5 18:14

import os
import re
import time,requests
from queue import Queue
import  threading
from urllib import parse

import numpy as np
import xlwt
import pandas as pd
from lxml import etree
from selenium.webdriver.chrome.options import Options
from selenium import  webdriver
class Thread_shop(threading.Thread):
    def __init__(self,pageQueue,shopQueue):
        super(Thread_shop, self).__init__()
        self.pageQueue=pageQueue
        self.shopQueue=shopQueue
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
            'cookie': 'shshshfpa=4d5362d2-9274-48f7-cb9d-6b4ca09659fc-1613742968; shshshfpb=hWNjkmtDXb7L6UUM3qKRbeQ==; __jdu=1613742966735844808257; areaId=1; ft_qgd=1614259330000; unpl=V2_ZzNtbRECEUEnAUADLBsPUWIGEVsRUkIXJQpCU3sdDgc1AEBdclRCFnUURldnGF8UZgsZXUNcRhRFCEdkeRtVB2QGFl5KZ3Mldgh2VUsZWwVlBRdeSlBEE3cMT1F+EF0MZAcUbXJQQxxFOHZUcxxcBmECEl5EZ0IldglFVnwQVAJiAiIWLFYOFXIIRFJ+GlQCYAUQWUtSRhx0AUVQfSldNWQ=; __jdv=122270672|jd.dlads.cn|t_338324529_|tuiguang|bdcec87ff3be4427b403a35615c3c2c1|1638407442029; mt_xid=V2_52007VwMVUl9eV1kXTh5aB2MKF1dUWVtZG08pWlZnBBtaCVhODxhBHUAAbwoTTlUMAVIDHhFVVzMBQFtcCwZeL0oYXwV7AxFOXFxDWhdCG1oOZAoiUG1YYl8ZTxtYAmMAE1RtWFtbGw==; ipLoc-djd=1-72-55666-0; TrackID=13m1Dg2m5iVemH9sU3PGHfYGruW9hagcufkPtJbE6hCn5VM4s1qkAtTimJ9G4Cb0aTyCpYOryzQG6KBI7wGgdfUPCaU0bTVKufk_g4g4yz7Y; _pst=jd_69457f533060e; unick=jd_69457f533060e; pin=jd_69457f533060e; _tp=OFZbFUgHoPNona7lsSOKlFeS/N2GG546m313PQeBs3Y=; PCSYCityID=CN_430000_430200_0; __jda=122270672.1613742966735844808257.1613742967.1638785701.1639053490.20; shshshfp=026b3689fa3e5c8c50ec398c514adfc1; __jdc=122270672; ip_cityCode=1488; wlfstk_smdl=ecany346ibultrtoz11zuyastf95tgv7; logintype=qq; npin=jd_69457f533060e; thor=A1DAF9A3771C28F1613BC278CB2DA1F5AEFA3D2559D3AF31BEB8D439EBA5152D6C9630E5D2796AD7FD8F3E0186DBB0164C5C6578757C086E1C7C454A2EA01741528E3462401241BEE4797288D08C88A53DE2D8128C5A7B7AB6F8CE2932417E37572D0C06B0269938293FDA865EEA79AE11F622F7BAD9AA92DD0761EE5835B22B15105866966AEDE7A31B9C7EFB707E4763086E2ADBC1117FB4E2BF13D43D4C2E; pinId=wd-CpkDL8qBPam5wBhI1lrV9-x-f3wj7; token=e01ae8c3a4eceab006c46eb1473e7904,3,910587; __tk=XcuFupu1ZsuFYSnSYsayZpkyZpGyYSh5Y3axXUbRXS2,3,910587; shshshsID=d9b7e590179c4b12df7bba3342ac4565_22_1639057017346; __jdb=122270672.25.1613742966735844808257|20.1639053490; 3AB9D23F7A4B3C9B=6K466RDB6BXLGSJS6D5PGMA6RPFIZK3YX7I4ONZMK2N6P2PAQDI3JOLCL5Z26X6XIFUIRVJ6U6L5QMCGCBOPEZXNPE'}

    def run(self):
        while True:

            if self.pageQueue.empty():
                break
            page_url=self.pageQueue.get()
            self.parse(page_url)

    # 获取每页的商品链接
    def parse(self,page_url):
        resp = requests.get(page_url, headers=self.headers).content
        html = etree.HTML(resp)
        # 商品列表
        li_list = html.xpath('//*[@id="J_goodsList"]/ul/li')
        for li in li_list:
            # 选择链接元素
            id = li.xpath('./@data-sku')
            # 拼接
            shop_url = 'https://item.jd.com/' + str(id[0]) + '.html'
            # 将商品链接添加到队列
            self.shopQueue.put(shop_url)


class Thread_sourse(threading.Thread):

    def __init__(self, pageQueue, shopQueue):
        super(Thread_sourse, self).__init__()
        self.pageQueue = pageQueue
        self.shopQueue = shopQueue

        options = Options()
        self.driver = webdriver.Chrome(options=options)

    def run(self):
        while True:
            if self.shopQueue.empty():
                break
            shop_url=self.shopQueue.get()
            self.parse(shop_url)

    def parse(self,shop_url):
        # 访问商品对应链接
        self.driver.get(shop_url)
        time.sleep(0.5)
        # 点击评论
        self.driver.find_element_by_xpath('//*[@id="detail"]/div[1]/ul/li[4]').click()
        time.sleep(0.5)
        # 判断评价页是否存在
        c = self.driver.find_elements_by_xpath('//*[@class="percent-con"]')
        if not c:
            # 由于某些促销产品的评论位置不一样
            self.driver.find_element_by_xpath('//*[@id="detail"]/div[1]/ul/li[5]').click()
            time.sleep(0.5)
        # 获取网页源代码
        resp_shop = self.driver.page_source
        html = etree.HTML(resp_shop)
        items = {}
        # 获取商品名称
        shop_name = html.xpath('//*[@class="sku-name"]/text()')
        for i in range(len(shop_name)):
            # 正则表达式去除前后空格
            shop_name[i] = re.sub("^\s+|\s+$", "", shop_name[i])
        # 由于清洗后某些商品列表长度为n存在n-1个空值 这里删除空值的作用
        shop_name = [i for i in shop_name if i != '']
        price = html.xpath('//*[@class="p-price"]/span[2]/text()')
        name = html.xpath('//*[@id="crumb-wrap"]/div/div[2]/div[2]/div[1]/div/a/text()')
        sale = html.xpath('//*[@id="comment-count"]/a/text()')  # 销量
        good = html.xpath('//*[@class="percent-con"]/text()')  # 好评度
        good_count = html.xpath('//*[@id="comment"]/div[2]/div[2]/div[1]/ul/li[5]/a/em/text()')  # 好评数
        bad_count = html.xpath('//*[@id="comment"]/div[2]/div[2]/div[1]/ul/li[7]/a/em/text()')  # 差评数
        comment = html.xpath('//*[@class="tag-list tag-available"]/span/text()')
        # print(shop_name,price,name,sale,good,good_count,bad_count,bad_count)
        for i in range(len(comment)):
            # 正则表达式 去除英文 数字 和()
            comment[i] = re.sub("[A-Za-z0-9\(\)]", "", comment[i])
        for shop_name_,price_, name_, sale_, good_, good_count_, bad_count_ in zip(shop_name,price, name, sale, good, good_count, bad_count):
            items['商品名称'] = shop_name_
            items['价格'] = price_
            items['店铺名称'] = name_
            items['销量'] = sale_.replace('(', '').replace(')', '').replace('+', '')
            items['好评数'] = good_count_.replace('(', '').replace(')', '').replace('+', '')
            items['差评数'] = bad_count_.replace('(', '').replace(')', '').replace('+', '')
            items['好评度'] = good_.replace('(', '').replace(')', '').replace('+', '')
            # 在每个元素后面添加分隔符-
            comment = "-".join(comment)
            items['评价'] = comment
        print(items)
        # 如果文件不存在则添加表头
        if not os.path.exists('D:\\jdshop.csv'):
            # 如果使用所有标量值，则必须传递索引(ability) index=0
            pd.DataFrame(items, index=[0]).to_csv('D:\\jdshop.csv', mode='a', encoding='utf_8_sig',
                                                 index=False)  # index=False  去除序号
        else:
            pd.DataFrame(items, index=[0]).to_csv('D:\\jdshop.csv', mode='a', encoding='utf_8_sig', index=False,
                                                 header=False)
def main():
    pageQueue=Queue(100)
    shopQueue=Queue(100)

    url='https://search.jd.com/Search?keyword='+parse.quote(input("输入需要爬取的商品名称"))+'&enc=utf-8&suggest=1.def.0.base&wq=%E7%AC%94%E8%AE%B0%E6%9C%ACdn&pvid=06db172b26c2486cbeb19343dfbbd783'
    for i in range(1,200):
        if(i%2!=0):
            page_url=url+str(i)
            pageQueue.put(page_url)
    for i in range(5):
        t1=Thread_shop(pageQueue,shopQueue)
        t1.start()
    for i in range(5):
        t2=Thread_sourse(pageQueue,shopQueue)
        t2.start()

if __name__ == '__main__':
    main()

