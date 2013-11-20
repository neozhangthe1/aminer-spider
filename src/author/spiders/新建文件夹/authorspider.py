from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
#from tutorial.items import EssayInfo
#from tutorial.agents import AGENTS
#from tutorial.proxy import PROXIES
import urllib2,urllib,socket
from scrapy.http.cookies import CookieJar
from author.PriorityPeople import PriorityPeople
from author.getpp import buildPP
from author.agents import AGENTS
#from scrapy.item import Item, Field
from scrapy.http import Request
from scrapy.http import FormRequest
import MySQLdb
import time
import pymongo
import types
import urllib2
import cookielib
import re
import random
import time
import string
import os
class authorspider(BaseSpider):
    handle_httpstatus_list=[302,503,200,307,403]
    name = 'authorspider'
    #allowed_domains = ['scholar.google.com']
    conn = pymongo.Connection(host='10.1.1.111',port=12345)
    #conn = pymongo.Connection(host='166.111.134.53',port=12345)
    db = conn['arnet_db']
    table = db['account']
    error = db['errorlist1']
    dproxy = db['prorxy']
    #connect to the mongo database, adaptable when needed
    conn_my = MySQLdb.connect(host="10.1.1.110",user="root",passwd="keg2012",db="arnet_db")
    #conn_my = MySQLdb.connect(host="166.111.134.53",user="root",passwd="keg2012",db="arnet_db")
    cursor = conn_my.cursor()
    #connect to the MySQL database, adaptable when needed
    id = lambda x:''.join(random.sample(string.hexdigits,16)).lower()
    def __init__(self):
      self.start_pointer = self.startpointer()
      self.proxy=''
      self.a = buildPP()
      self.pp = self.a.getpp(3)
      self.ppointer = self.getppointer()
      self.proxy_usetime = 0
      self.changep()
      self.crawlli=[]

    def start_requests(self):
      yield self.startnext(self.start_pointer-1)
      self.crawlli.append(self.start_pointer-1)



    def parse(self,response):
      print response.meta['aid']
      cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
      cookieJar.extract_cookies(response, response.request)
      if self.proxy_usetime>=5:
        self.savep(response.meta['proxy'])
        self.changep()
      aid = response.meta['aid']
      pointer = response.meta['pointer']
      if response.status !=200:
        if response.meta['proxy'] == self.proxy:
          self.changep()      
        request = Request(response.url, dont_filter = True,callback = self.parse, meta = {'dont_redirect':True,'dont_retry':True,'User-agent':random.choice(AGENTS),'aid':aid,'proxy':self.proxy,'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'cookie_jar': cookieJar,'pointer':pointer})
        cookieJar.add_cookie_header(request) # apply Set-Cookie ourselves
        yield request

      if response.status ==200 :
        self.proxy_usetime+=1
      	print 'successfully'
      	hxs = HtmlXPathSelector(response)
      	authorpage = hxs.select('//td[contains(@valign,"top")]').select('a/@href').extract()
      	if len(authorpage) >= 2:
          self.table.insert({'_id':aid,'pages':authorpage,'account':True})
        else:
          self.table.insert({'_id':aid,'account':False,'reason':'Not Found'})
        if pointer not in self.crawlli:
          yield self.startnext(pointer)
          self.crawlli.append(pointer)
        if (pointer+1) not in self.crawlli:
          yield self.startnext(pointer+1)
          self.crawlli.append(pointer+1)
    def next(self,pointer):
      aid = PriorityPeople[pointer]
      name = self.aname(aid)
      if name:
        names = name.split(',')      
        if len(names) == 1:
          query = 'author:"%s"'%names[0].replace(' ','+')
          url = 'http://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors=%s'%query
          return Request(url,dont_filter = True,callback = self.parse,meta={'dont_retry':True,'dont_redirect':True,'proxy':self.proxy,'User-agent':random.choice(AGENTS),'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'aid':aid,'pointer':pointer})
        elif len(names) == 2:
          query = 'author:"%s" OR author:"%s"'%(names[0].replace(' ','+'),names[1].replace(' ','+'))
          url = 'http://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors=%s'%query
          return Request(url,dont_filter = True,callback = self.parse,meta={'dont_retry':True,'dont_redirect':True,'proxy':self.proxy,'User-agent':random.choice(AGENTS),'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'aid':aid,'pointer':pointer})
        elif len(names) == 3:
          query = 'author:"%s" OR author:"%s" OR author:"%s"'%(names[0].replace(' ','+'),names[1].replace(' ','+'),names[2].replace(' ','+'))
          url = url = 'http://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors=%s'%query
          return Request(url,dont_filter = True,callback = self.parse,meta={'dont_retry':True,'dont_redirect':True,'proxy':self.proxy,'User-agent':random.choice(AGENTS),'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'aid':aid,'pointer':pointer})
        else:
          self.table.insert({'_id':aid,'account':False,'reason':'multiple names'})
          return False
      else:
        return False

    def aname(self,aid):
      self.cursor.execute("select names from na_person where id = %d"%aid)
      authorname = self.cursor.fetchall()
      if authorname == [] or len(authorname) == 0:
        self.table.insert({'_id':aid,'account':False,'reason':'Database False'})
        return False
      else:
        while type(authorname) is list or type (authorname) is tuple:
          authorname = authorname[0]
        return authorname
    def startpointer(self):
      a = 0
      while True:
        aid = PriorityPeople[a]
        if self.table.find_one({'_id':aid}) is not None:
          a += 1
          continue
        else:
          print 'start at',PriorityPeople[a]
          return a
    def changep(self):
      print 'changing proxy'
      socket.setdefaulttimeout(3.0)
      test_url = 'http://scholar.google.com.hk/scholar?q=Hoffman&btnG=&hl=zh-CN&as_sdt=0%2C5'
      self.ppointer+=1
      if self.ppointer == (len(self.pp) +1):
        self.ppointer = 0
      while True:

        proxy = self.pp[self.ppointer]
        proxy =  'http://'+proxy
        try:
          start = time.time()
          f = urllib.urlopen(test_url,proxies={'http':proxy})
          f.close()
        except:
          self.ppointer+=1
          continue
        else:
          end=time.time()
          dur = end - start
          print proxy,dur
          if dur <= 3:
            print 'proxy changed to'
            print proxy
            self.proxy = proxy
            self.proxy_usetime =0
            fw=open(r'C:\Python27\author\author\ppointer.txt','w')
            fw.write('%d'%self.ppointer)
            fw.close()
            break
    def savep(self,proxy):
      fr = open(r'C:\Python27\author\author\validp.txt','r')
      p = []
      for i in fr.readlines():
        p.append(i)
      fr.close()
      fw = open(r'C:\Python27\author\author\validp.txt','w')
      for i in p:
        fw.write(i)
      proxy = proxy.replace('http://','')
      fw.write(proxy)
      #fw.write(proxy+'\n')
      fw.close()
    def getppointer(self):
      fr = open(r'C:\Python27\author\author\ppointer.txt','r')
      p = fr.readline()
      fr.close()
      if p is '':
        p = 0
      else:
        p = int(p)
      return p
    def startnext(self,pointer):
      i = 1
      while True:
        request = self.next(pointer+i)
        if request:
          return request
        else:
          i+=1



      	#print 'http://scholar.google.com' + authorpage[1]
