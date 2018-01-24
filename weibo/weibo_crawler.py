#python3
#-*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import urllib.request
import json
#import pymysql
import time
import datetime
import os
#林志颖的微博首页url
url = "https://weibo.com/dreamerjimmy?is_hot=1"
proxy_addr = "116.54.78.3:8118"  #代理ip 偶尔会被强制block，当被强制block时需修改此处的ip和端口

teacher_id = '2044075383' #老师的微博id
wb_id = '1713926427' #微博搞笑排行榜
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
class Comments(object):
    '''评论相关信息'''
    userid='' #用户的id
    user_name = ''
    comment_text = ''
    source = '' #发送评论的设备
    verified = ''  # 是否认证
    like_counts = '' #点赞数量

def getUserInfo(id):
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
    #file_name = userInfo.screen_name+'.jpg'
    
    #save_img(user_info.get('profile_image_url'),userInfo.screen_name)
    print(
        "微博昵称：" + userInfo.screen_name + "\n" + "微博主页地址：" + userInfo.profile_url + "\n"
        + "微博头像地址：" + userInfo.profile_image_url + "\n" + "是否认证：" + str(userInfo.verified) + "\n"
        + "微博说明：" + userInfo.description + "\n"
        + "关注人数：" + str(userInfo.follow_count) + "\n" + "粉丝数：" + str(userInfo.followers_count) + "\n"
        + "性别：" + userInfo.gender + "\n" + "微博等级：" + str(userInfo.urank) + "\n")

    return userInfo
path = './profile_image/'



# 获取微博主页的containerid，爬取微博内容时需要此id
def get_containerid(url):
    data = use_proxy(url, proxy_addr)
    content = json.loads(data)
    for data in content.get('data').get('tabsInfo').get('tabs'):
        if data.get('tab_type') == 'weibo':
            containerid = data.get('containerid')
    return containerid

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

def get_latest10_comments(comments_url):
    #获取最新的10条评论，返回json格式的数据，其中包括用户的信息，评论内容，获赞的数量
    comments = Comments()
    data = use_proxy(comments_url,proxy_addr)
    content = json.loads(data)
    latest10_comments = content.get('data').get('data')
    if len(latest10_comments)>0:
        for i in range(len(latest10_comments)):
            comments.userid = latest10_comments[i].get('user').get('id')
            #print(comments.userid)
            comments.user_name = latest10_comments[i].get('user').get('screen_name')
            #print(comments.user_name)
            comments.comment_text = latest10_comments[i].get('text')
            #print(comments.comment_text)
            comments.source = latest10_comments[i].get('source')
            comments.verified = latest10_comments[i].get('verified')
            comments.like_counts = latest10_comments[i].get('like_counts')
            with open('out.txt', 'a', encoding='utf-8') as fh:
                fh.write("----第" +  str(i) + "条评论----" + "\n")
                fh.write("评论用户：" + str(comments.user_name) + "\n" +
                            "用户id：" + str(comments.userid) + "\n" + "评论内容：" + comments.comment_text + "\n" +
                            "点赞数：" + str(comments.like_counts) + "\n" + "设备：" + str(
                        comments.source) +
                        "\n" + "是否微博认证：" + str(comments.verified) + "\n")
                if i == len(latest10_comments)-1:
                    fh.write('---------------------------------------------------------------------'+"\n")
     
    
    

    return comments

def get_hot10_comments(comments_url):
    #获取热评的10条评论，返回json格式的数据，其中包括用户的信息，评论内容，获赞的数量
    data = use_proxy(comments_url,proxy_addr)
    content = json.loads(data)
    hot10_comments = content.get('data').get('hot_data')
    if len(hot10_comments)>0:
        for i in range(len(hot10_comments)):
            comments.userid = hot10_comments[i].get('user').get('id')
            #print(comments.userid)
            comments.user_name = hot10_comments[i].get('user').get('screen_name')
            #print(comments.user_name)
            comments.comment_text = hot10_comments[i].get('text')
            #print(comments.comment_text)
            comments.source = hot10_comments[i].get('source')
            comments.verified = hot10_comments[i].get('verified')
            comments.like_counts = hot10_comments[i].get('like_counts')
            with open('out_hot10.txt', 'a', encoding='utf-8') as fh:
                fh.write("----第" +  str(i) + "条评论----" + "\n")
                fh.write("评论用户：" + str(comments.user_name) + "\n" +
                            "用户id：" + str(comments.userid) + "\n" + "评论内容：" + comments.comment_text + "\n" +
                            "点赞数：" + str(comments.like_counts) + "\n" + "设备：" + str(
                        comments.source) +
                        "\n" + "是否微博认证：" + str(comments.verified) + "\n")    
    
    return hot10_comments

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

#暂时不要有下边的方法，有错
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

if __name__ == "__main__" :
    '''
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    info = soup.find_all(class_="PCD_person_info")
    print(soup)
    #userInfo = getUserInfo(wb_id)
    '''
    '''
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=1259110474&containerid=1076031259110474&page=1'
    data = use_proxy(weibo_url, proxy_addr)
    content = json.loads(data)
    cards = content.get('data').get('cards')
    mblog = cards[1].get('mblog')
    #weibo_text = mblog.get('text')
    print(cards[7])
    '''
    #获得老师的微博基本信息
    userInfo = get_userInfo(teacher_id)
    print(userInfo)    
    #测试获取评论的方法，page=1时才存在hot_comments
    # weibo_content_id 分别为5条微博的：4199428388589007，4199439113220988，4199664431915031，4199454695249390，4199456381598466
    #时间是1.24 16:05
    weibo_content_id = '4199456381598466'
    page = '1'
    comments_url = 'https://m.weibo.cn/api/comments/show?id=%s&page=%s'%(weibo_content_id,page)
    comments = Comments()
    comments = get_latest10_comments(comments_url)
    hot_comments = Comments()
    hot_comments = get_hot10_comments(comments_url)
    

    