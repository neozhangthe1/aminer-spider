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


class Titlespider(BaseSpider):
    
    handle_httpstatus_list=[302,503,200,307,403]
    name = 'proxytest'
    #allowed_domains = ['scholar.google.com']
    conn = pymongo.Connection(host='166.111.134.53',port=12345)
    #conn = pymongo.Connection(host='166.111.134.53',port=12345)
    db = conn['arnet_db']
    table = db['proxyt']
    error = db['errorlist1']
    dproxy = db['prorxy']
    #connect to the mongo database, adaptable when needed
    conn_my = MySQLdb.connect(host="166.111.134.53",user="root",passwd="keg2012",db="arnet_db")
    #conn_my = MySQLdb.connect(host="166.111.134.53",user="root",passwd="keg2012",db="arnet_db")
    cursor = conn_my.cursor()
    #connect to the MySQL database, adaptable when needed
    id = lambda x:''.join(random.sample(string.hexdigits,16)).lower()
    def __init__(self):
      self.aidpointer = self.startpointer()
      self.start_aid = PriorityPeople[self.aidpointer]#self.def_start_id()
      self.authorname = self.aname(self.start_aid)   
      self.authornameList = self.seperateName(self.authorname)
      self.initial(self.authorname,self.start_aid,self.authornameList)
      self._authornameList = self.ListChange(self.authornameList)
      self.start_urls = ["http://scholar.google.com/scholar?hl=en&num=100&as_sdt=0,5&q=%s"%s for s in self._authornameList]
      
      self.timepointer = int(time.clock())
      self.crawled_id=[]
      self.pages = 0
      self.proxy=''
      self.a = buildPP()
      self.pp = self.a.getpp(1)
      self.ppointer_test = self.getppointer()
      self.proxy_usetime = 0
      self.changep()
      self.crawlli=[]
      
      
      


    def start_requests(self):
      self.crawlli.append(self.aidpointer)
      for url in self.start_urls:
        req = Request(url,dont_filter = True,callback = self.parse,meta={'proxy':self.proxy,'dont_retry':True,'dont_redirect':True,'User-agent':random.choice(AGENTS),'aid':self.start_aid,'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'pointer':self.aidpointer})
        print req.meta['proxy']

        yield req

    def parse(self, response):
      cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
      cookieJar.extract_cookies(response, response.request)
      aid = response.meta['aid']
      pointer = response.meta['pointer']     
      if response.status != 200 and response.status!=404 :
        print 'proxy %s does not work'%response.meta['proxy']
        print 'failed'
        print response.url  
        if response.meta['proxy'] == self.proxy:
          self.changep()      
        request = Request(response.url, dont_filter = True,callback = self.parse, meta = {'dont_redirect':True,'dont_retry':True,'User-agent':random.choice(AGENTS),'aid':self.start_aid,'proxy':self.proxy,'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'cookie_jar': cookieJar,'pointer':pointer})
        cookieJar.add_cookie_header(request) # apply Set-Cookie ourselves
        yield request
      if response.status ==404 or response.url== 'http://scholar.google.com/None':
        if response.meta['proxy'] == self.proxy:
          self.changep()
        print '*****************************************************************'
        print '%d procedure is finished'%aid
        print '*****************************************************************'
        requests = self.start_next(pointer)
        for request in requests:
          yield request


      if response.status ==200: 
        self.proxy_usetime+=1
        if self.proxy_usetime>=3:
          self.savep(response.meta['proxy'])
          self.changep()
        print 'successfully'
        hxs = HtmlXPathSelector(response)
        if self.get_follow_url is None :
          print '*****************************************************************'
          print '%d procedure is finished'%aid
          print '*****************************************************************'
          requests = self.start_next(pointer)
          for request in requests:
            yield request

        else:
          request = Request("http://scholar.google.com/%s"%self.get_follow_url(hxs),dont_filter = True,callback = self.parse,meta={'dont_merge_cookies':True,'dont_retry':True,'dont_redirect':True,'proxy':self.proxy,'User-agent':random.choice(AGENTS),'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'aid':aid,'cookie_jar': cookieJar,'pointer':pointer})
          cookieJar.add_cookie_header(request)
          print "http://scholar.google.com/%s"%self.get_follow_url(hxs)
          yield request
 


    def get_follow_url(self,hxs):#return the essential part of next url, by extract the 'nextPage' information from the original url
      relative_url = hxs.select('//td[contains(@align,"left")]').select('a/@href').extract()
      if relative_url == []:
        return None
  
      else:
        relative_url = relative_url[0]
        return relative_url

    def aname(self,aid):
      self.cursor.execute("select names from na_person where id = %d"%aid)
      authorname = self.cursor.fetchall()
      while type(authorname) is list or type (authorname) is tuple:
        authorname = authorname[0]
      return authorname

    def initial(self,List,aid,authornameList):
      if type(List) is list:
        for name in List:
          self.table.insert({'_id':name,'paper':[]})
      if type(List) is str:
        check = 0
        _list = ''
        for i in List:
          if i <= chr(127):
            _list = _list + i
        print _list
        #self.table.insert({'_id':aid,'paper':[],'name':_list})
    
    def ListChange(self,AuthorList):
      if type(AuthorList) is list:
        _AuthorList=[]
        for name in AuthorList:
          name = name.replace(' ','+')
          _AuthorList.append(name)
        return _AuthorList
      if type(AuthorList) is str:
        return AuthorList.replace(' ','+')

    def seperateName(self,name):
      nameList = name.split(',')
      return nameList

    def checktime(self):
      a = int(time.clock())
      if (a - self.timepointer) >= self.interval:
        self.timepointer = a
        return True
      else:
        return False

    def start_next(self,iid):
      '''
      generate requests by given aid
      return requests as a list. if name already exists in pubtable, return empty request list.
      '''

      pointer = iid
      pointer+=1
      _aid = False
      requests = []


      for i in range(1,4):
        if pointer not in self.crawlli:
          _aid = PriorityPeople[pointer]
          self.crawlli.append(pointer)
          break
        pointer+=1
      if _aid:
        self.cursor.execute("select names from na_person where id = %d"%_aid)
        name = self.cursor.fetchall()
        while type(name) is list or type (name) is tuple:
          name = name[0]        
        print '************************************'
        print 'start crawling %s'%name
        print '************************************'
        authorname = self.aname(_aid)  
        authornameList = self.seperateName(authorname)
        self.initial(authorname,_aid,authornameList)
        _authornameList = self.ListChange(authornameList)
        query = self.modify(_authornameList)
        request1 = Request("http://scholar.google.com/scholar?start=0&q=%s&hl=en&num=100&as_sdt=0,5"%query,dont_filter = True, callback = self.parse,meta={'User-agent':random.choice(AGENTS),'aid':_aid,'proxy':self.proxy,'dont_retry':True,'dont_redirect':True,'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'pointer':pointer})
        request2 = Request("http://scholar.google.com/scholar?start=500&q=%s&hl=en&num=100&as_sdt=0,5"%query,dont_filter = True, callback = self.parse,meta={'User-agent':random.choice(AGENTS),'aid':_aid,'proxy':self.proxy,'dont_retry':True,'dont_redirect':True,'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'pointer':pointer})
        requests.append(request1)
        requests.append(request2)
   #   self.crawlli.append(_aid)
      return requests
    def modify(self,nameList):
      if len(nameList) == 1:
        q = 'author:"%s"'%nameList[0]
      if len(nameList) >= 2:
        i = 0
        q = 'author:"%s"'%nameList[0]
        for name in nameList:
          if i != 0:
            q = q+'OR author:"%s"'%name
          i+=1
      return q



    def check_error_list(self):
      '''
      check the 10th latest crawled author in pubcollection before a id, return the length of error collection
      '''
      checkid = self.aidpointer - self.delay
      if checkid >= 0 and self.table.find_one({'_id':checkid}) is not None:
        num = len(self.table.find_one({'_id':checkid}).get('paper'))
        name = self.table.find_one({'_id':checkid}).get('name')
        if num < self.threshold:
          self.table.remove({'_id':checkid})
          if self.error.find_one({'_id':checkid}) is None:
            self.error.insert({'_id':checkid,'name':name,'pnum':num,'trytimes':0})
          else:
            self.error.update({'_id':checkid},{"$set":{'pnum':num}})
      return self.error.find().count()

    def counterror(self):
      num = 0
      errors = self.error.find()
      for error in errors:
        if error['trytimes'] < self.trytimes:
          num += 1
      return num

    def def_start_id(self):
      start = 0
      if self.table.find() is not None:
        for i in self.table.find().sort("_id",pymongo.DESCENDING):
          start = i['_id'] + 1
          break
      if start >=0:
        print 'now start crawling id %d'%start
        return start
      else:
        print 'now start crawling id %d'%0
        return 0
    def threshold(self,aid):
      self.cursor.execute('select pid from na_author2pub where aid = "%s"'%aid)
      pids = self.cursor.fetchall()
      pidList=[]
      for perid in pids:
        pidList.append(perid[0])
      num = (len(pidList))
      return num
    def startpointer(self):
      a = 0
      while True:
        aid = PriorityPeople[a]
        if self.table.find_one({'_id':aid}) is not None:
          a += 1
          continue
        else:
          return a

    def changep(self):
      print 'changing proxy'
      socket.setdefaulttimeout(3.0)
      test_url = 'http://scholar.google.com.hk/scholar?q=Hoffman&btnG=&hl=zh-CN&as_sdt=0%2C5'
      self.ppointer_test+=1
      if self.ppointer_test == (len(self.pp) +1):
        self.ppointer_test = 0
      while True:

        proxy = self.pp[self.ppointer_test]
        proxy =  'http://'+proxy
        try:
          start = time.time()
          f = urllib.urlopen(test_url,proxies={'http':proxy})
          f.close()
        except:
          self.ppointer_test+=1
          continue
        else:
          end=time.time()
          dur = end - start
          print proxy,dur
          if dur <= 2:
            print 'proxy changed to'
            print proxy
            self.proxy = proxy
            self.proxy_usetime =0
            fw=open(r'C:\Python27\author\author\ppointer_test.txt','w')
            fw.write('%d'%self.ppointer_test)
            fw.close()
            break
    def savep(self,proxy):
      fr = open(r'C:\Python27\author\author\validpback.txt','r')
      p = []
      for i in fr.readlines():
        p.append(i)
      fr.close()
      fw = open(r'C:\Python27\author\author\validpback.txt','w')
      for i in p:
        fw.write(i)
      proxy = proxy.replace('http://','')
      #fw.write(proxy)
      fw.write(proxy+'\n')
      fw.close()
    def getppointer(self):
      fr = open(r'C:\Python27\author\author\ppointer_test.txt','r')
      p = fr.readline()
      fr.close()
      if p is '':
        p = 0
      else:
        p = int(p)
      return p
