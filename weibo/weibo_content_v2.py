# -*- coding: utf-8 -*-

import urllib.request
import json
#import pymysql
import time
import datetime
# import re

# 定义要爬取的微博大V的微博ID
wb_id = '1259110474'  # 赵丽颖
# wb_id = '1192329374'  # 谢娜
# wb_id = '2044075383'  # myself
# 设置代理IP
# 网上有很多免费代理ip，如西刺免费代理IPhttp://www.xicidaili.com/，自己可找一个可以使用的进行测试；
proxy_addr = "61.135.217.7:80"

'''
def connect_to_mysql():
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='123',
        db='sina_weibo',
        charset='utf8mb4'
    )
    return conn
'''

class UserInfoItem(object):
    """关注对象的相关个人信息"""
    wb_id = ''  # 用户ID
    crawl_time = ''  # 爬取时间
    screen_name = ''  # 微博昵称
    gender = ''  # 性别
    follow_count = []  # 关注数
    followers_count = []  # 粉丝数
    description = ''  # 个人描述
    urank = []  # 微博等级
    profile_url = ''  # 主页链接
    profile_image_url = ''  # 微博头像地址
    verified = []  # 是否认证



class WeiboItem(object):
    """所发微博信息"""
    wb_id = ''  # 用户ID
    mblogid = ''  # 发布微博ID
    crawl_time = ''  # 爬取时间
    ori_created_at = ''  # 发布时间
    created_date = ''  # 发布日期
    text = ''  # 微博内容
    attitudes_count = []  # 点赞数
    comments_count = []  # 评论数
    reposts_count = []  # 转发数
    scheme = ''  # 微博地址

    def transform_date(self):
        crawl_datetime = datetime.datetime.fromtimestamp(self.crawl_time)
        if self.ori_created_at.__contains__('昨天'):
            self.created_date = crawl_datetime - datetime.timedelta(days=1)
        elif self.ori_created_at.__contains__('小时前'):
            local_delta = int(self.ori_created_at[0:self.ori_created_at.find('小时前')])
            self.created_date = crawl_datetime - datetime.timedelta(hours=local_delta)
        elif self.ori_created_at.__contains__('分钟前'):
            local_delta = int(self.ori_created_at[0:self.ori_created_at.find('分钟前')])
            self.created_date = crawl_datetime - datetime.timedelta(minutes=local_delta)
        else:
            if len(self.ori_created_at) <= 5:
                full_date = str(datetime.datetime.now().year) + '-' + self.ori_created_at
                self.created_date = datetime.datetime.strptime(full_date, '%Y-%m-%d')
            else:
                self.created_date = datetime.datetime.strptime(self.ori_created_at, '%Y-%m-%d')

        return self.created_date


def insert_userInfo(conn, userInfo):
    """ 向数据库插入userInfo """
    print("开始写入个人信息")
    try:
        conn.cursor().execute(
            "INSERT INTO user_info (wb_id, crawl_time, screen_name, gender, follow_count, followers_count, \n"
            "description, urank, profile_url, profile_image_url, verified) \n"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                userInfo.wb_id,
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(userInfo.crawl_time)),
                userInfo.screen_name,
                userInfo.gender,
                str(userInfo.follow_count),
                str(userInfo.followers_count),
                userInfo.description,
                str(userInfo.urank),
                userInfo.profile_url,
                userInfo.profile_image_url,
                str(int(userInfo.verified))
            )
        )
        conn.commit()
        print("写入完成")
    except pymysql.Error as e:
        print("出现错误")
        print("Error %d: %s" % (e.args[0], e.args[1]))

    return conn


def insert_weibo(conn, weiboItemList):
    """ 向数据库插入weibo"""
    print("写入微博信息")
    count = -1
    failure_weiboItemList = []
    for weiboItem in weiboItemList:
        count += 1
        try:
            conn.cursor().execute(
                "INSERT INTO weibo_item (wb_id, mblog_id, crawl_time, created_date, content, \n"
                "attitudes_count, comments_count, reposts_count, scheme) \n"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    weiboItem.wb_id,
                    weiboItem.mblogid,
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(weiboItem.crawl_time)),
                    weiboItem.created_date.strftime('%Y-%m-%d'),
                    weiboItem.text,
                    str(weiboItem.attitudes_count),
                    str(weiboItem.comments_count),
                    str(weiboItem.reposts_count),
                    weiboItem.scheme
                )
            )
            conn.commit()

        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            failure_weiboItemList.append(weiboItem)
            print('[%d]:%s'% (count, weiboItem.text))

    print("写入完成%d, 写入失败%d" % (len(weiboItemList)-len(failure_weiboItemList), len(failure_weiboItemList)))
    return conn, failure_weiboItemList


# 定义页面打开函数
def use_proxy(url, proxy_addr):
    req = urllib.request.Request(url)
    req.add_header("User-Agent",
                   """Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)
                   Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0""")
    proxy = urllib.request.ProxyHandler({'http': proxy_addr})
    opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    data = urllib.request.urlopen(req).read().decode('utf-8') #, 'ignore'
    return data


# 获取微博主页的containerid，爬取微博内容时需要此id
def get_containerid(url):
    data = use_proxy(url, proxy_addr)
    content = json.loads(data)
    for data in content.get('data').get('tabsInfo').get('tabs'):
        if data.get('tab_type') == 'weibo':
            containerid = data.get('containerid')
    return containerid


# 获取微博大V账号的用户基本信息，如：微博昵称、微博地址、微博头像、关注人数、粉丝数、性别、等级等
def get_userInfo(id):
    userInfo = UserInfoItem()
    url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + id
    data = use_proxy(url, proxy_addr)
    content = json.loads(data)
    user_info = content.get('data').get('userInfo')
    userInfo.wb_id = id
    userInfo.crawl_time = time.time()
    userInfo.screen_name = user_info.get('screen_name')
    userInfo.gender = user_info.get('gender')
    userInfo.follow_count = user_info.get('follow_count')
    userInfo.followers_count = user_info.get('followers_count')
    userInfo.description = user_info.get('description')
    userInfo.urank = user_info.get('urank')
    userInfo.profile_url = user_info.get('profile_url')
    userInfo.profile_image_url = user_info.get('profile_image_url')
    userInfo.verified = user_info.get('verified')

    print(
        "微博昵称：" + userInfo.screen_name + "\n" + "微博主页地址：" + userInfo.profile_url + "\n"
        + "微博头像地址：" + userInfo.profile_image_url + "\n" + "是否认证：" + str(userInfo.verified) + "\n"
        + "微博说明：" + userInfo.description + "\n"
        + "关注人数：" + str(userInfo.follow_count) + "\n" + "粉丝数：" + str(userInfo.followers_count) + "\n"
        + "性别：" + userInfo.gender + "\n" + "微博等级：" + str(userInfo.urank) + "\n")

    return userInfo

'''
# 获取微博内容信息,并保存到文本中，内容包括：每条微博的内容、微博详情页面地址、点赞数、评论数、转发数等
#url='https://m.weibo.cn/api/container/getIndex?type=uid&value=1259110474&containerid=1076031259110474&page=1'
def get_weibo(wb_id, out_file):
    global weiboItem
    weiboItemList = []
    output_text = 0
    i = 1
    while i < 2:
        url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + wb_id
        weibo_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + wb_id + '&containerid=' + \
                    get_containerid(url) + '&page=' + str(i)
        try:
            data = use_proxy(weibo_url, proxy_addr)
            content = json.loads(data)
            cards = content.get('data').get('cards')
            if len(cards) > 0:
                for j in range(len(cards)):
                    if cards[j].get('card_type') == 9:
                        weiboItem = WeiboItem()
                        mblog = cards[j].get('mblog')
                        weiboItem.wb_id = wb_id
                        weiboItem.crawl_time = time.time()
                        weiboItem.attitudes_count = mblog.get('attitudes_count')
                        weiboItem.comments_count = mblog.get('comments_count')
                        weiboItem.ori_created_at = mblog.get('created_at')
                        weiboItem.transform_date()
                        # weiboItem.created_at = transform_date(temp_created_at,)
                        weiboItem.reposts_count = mblog.get('reposts_count')
                        weiboItem.scheme = cards[j].get('scheme')
                        mblog_id_s = weiboItem.scheme.find('mblogid=')
                        weiboItem.mblogid = weiboItem.scheme[mblog_id_s+8:mblog_id_s+17]
                        weiboItem.text = mblog.get('text')
                        weiboItemList.append(weiboItem)
                        if output_text:
                            with open(out_file, 'a', encoding='utf-8') as fh:
                                fh.write("----第" + str(i) + "页，第" + str(j) + "条微博----" + "\n")
                                fh.write("微博地址：" + str(weiboItem.scheme) + "\n" +
                                         "发布时间：" + str(weiboItem.created_at) + "\n" + "微博内容：" + weiboItem.text + "\n" +
                                         "点赞数：" + str(weiboItem.attitudes_count) + "\n" + "评论数：" + str(
                                    weiboItem.comments_count) +
                                         "\n" + "转发数：" + str(weiboItem.reposts_count) + "\n")
                i += 1
            else:
                break
        except Exception as e:
            print(e)
            pass

    return weiboItemList

'''

if __name__ == "__main__":
    #file = "test.txt"
    #print(file)
    userInfo = get_userInfo(wb_id)
    print(userInfo)
    url_get_container = "https://m.weibo.cn/api/container/getIndex?type=uid&value=1259110474"
    container = get_containerid(url_get_container)
    print(container)
    #weiboItem = get_weibo(wb_id, file)
    #conn = connect_to_mysql()
    #conn = insert_userInfo(conn, userInfo)
    #conn, _ = insert_weibo(conn, weiboItem)
    #conn.close()
