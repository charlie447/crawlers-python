
#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import urllib
import urllib.request
import requests

import os
import re
import logging

'''data={}
data['word']='key words'

url_values=urllib.parse.urlencode(data)    #data is a list ,use urlencode(data) can convert "data" to String
url="http://www.baidu.com/s?"
full_url=url+url_values'''

full_url = "https://movie.douban.com/top250?start=0&filter="
for_get_url="https://movie.douban.com/top250?start=0&filter="
'''for i in range(0,writeableData.__len__()):       #convert every element in writeableData to Sting Type
    writeableData[i] = str(writeableData[i])

data2string = "".join(writeableData)'''
def parse_url_data(url):
    data=urllib.request.urlopen(url).read()
    data=data.decode('UTF-8')
    soup = BeautifulSoup(data, 'html.parser')

    #writeableData = soup.div.contents[1].contents[1].contents
    writeableData = soup.find(class_="review-content clearfix").p.string         #the content of this artical
def get_url_list(url):
    """
    get every top25 movie url list
    
    """
    links=[]
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    tags = soup.find_all(class_="hd")
    #links = tags.a.get("href")
    for tag in tags:
        link = tag.a.get("href")
        links.append(link)
    #print(links)
    #print(type(links))
    print(links)
    #print("****************************************")
    #print(type(tag))
    #print(type(links))
    return links
    '''urls = []
    for li in menu_tag.find_all("li"):
        url = "http://www.liaoxuefeng.com" + li.a.get('href')
        urls.append(url)
    return urls
    '''
def get_movie_name(info_url):
    '''
    this function returns a movie name
    '''
    response = requests.get(info_url)
    soup = BeautifulSoup(response.content, "html.parser")
    movie_name=soup.find("h1").span.string

    print(movie_name)
    return movie_name
def get_douban_rating(info_url):
    response = requests.get(info_url)
    soup = BeautifulSoup(response.content, "html.parser")
    rating = soup.find(class_="ll rating_num").string

    print(rating)
    return rating
def get_movie_info(info_url):
    '''
    this function returns a dictionary that contains some infomation
    of the movie  in the url
    '''
    response = requests.get(info_url)
    soup = BeautifulSoup(response.content, "html.parser")
    tags = soup.find(id="info").find_all("span")
    crewDict={}
    completeInfo = []
    for tag in tags:
        spans = tag.find_all("span")
        if spans==[]:
            continue
        jobs = []
        positions = spans[0].string
        #print(positions)
        ###################################
        aas= spans[1].find_all("a")
        crewList=[]
        for a in aas:
            #print(a.string)
            crewName=a.string
            crewList.append(crewName)

        crewString = " ".join(crewList)
        #######################################
        partInfo = positions + ":" +crewString
        completeInfo.append(partInfo)
        crewDict[positions]=crewList

    #print(spans[1].span.string)
    print(crewDict)

    #print("*******************************")
    #print(completeInfo)
    info = "\n".join(completeInfo)
    print(info)
    return info
    #infos =[]

    '''for info in tags[1:]:
        infos.append(info.find_all("span"))'''
    #print(tags)

    #print(infos)

if __name__ == '__main__':
    #save_test_txt(writeableData)
    #parse_url_data(full_url)
    links = get_url_list(for_get_url)
    #url = "https://movie.douban.com/subject/1291546/"
    #get_movie_info(url)
    #get_movie_name(url)
    #get_douban_rating(url)
    fo = open("test.txt","w+")     #open a txt file
    for url in links[0:23]:
        if url=="https://movie.douban.com/subject/5912992/" :
            continue
        movie_name=get_movie_name(url)
        fo.write(movie_name)
        fo.write("\n")
        douban_rating = get_douban_rating(url)
        fo.write(douban_rating)
        fo.write("\n")
        movie_info = get_movie_info(url)
        fo.write(movie_info)
        fo.write("\n")
        print("*****************BOUNDRY LINE****************")
        line = "*****************BOUNDRY LINE****************"
        fo.write(line)
        fo.write("\n")
    fo.close()
