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
from author._plist import Proxypool
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
class citationspider(BaseSpider):
    name = 'citationspider'
    #allowed_domains = ['scholar.google.com']
    conn = pymongo.Connection(host='10.1.1.111',port=12345)
    #conn = pymongo.Connection(host='166.111.134.53',port=12345)
    db = conn['arnet_db']
    table = db['pubication_test_3rd']
    table_account = db['account']
    error = db['errorlist1']
    dproxy = db['prorxy']
    #connect to the mongo database, adaptable when needed
    conn_my = MySQLdb.connect(host="10.1.1.110",user="root",passwd="keg2012",db="arnet_db",port=3306)
    cursor = conn_my.cursor()
    def __init__(self):
      self.timepointer = int(time.clock())
      self.proxy=''
      self.proxy_usetime = 0
      self.changep()
      self.aidpointer = self.startpointer()-1
      self.crawlli=[]
      self.startrequests = self.start_next(self.aidpointer)
    def start_requests(self):
    	for request in self.startrequests:
    		yield request

    def parse(self,response):
      cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
      cookieJar.extract_cookies(response, response.request)
      aid = response.meta['aid']
      pointer = response.meta['pointer']
      if response.status != 200:
        print 'proxy %s does not work'%response.meta['proxy']
        print 'failed'
        if response.meta['proxy'] == self.proxy:
          self.changep()      
        request = Request(response.url, dont_filter = True,callback = self.parse, meta = {'dont_redirect':True,'dont_retry':True,'User-agent':random.choice(AGENTS),'aid':aid,'proxy':self.proxy,'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'cookie_jar': cookieJar,'pointer':pointer})
        cookieJar.add_cookie_header(request) # apply Set-Cookie ourselves
        yield request
        self.proxy_usetime+=1
        if self.proxy_usetime>3:
          self.changep()
      if response.status == 200:
        paperList = self.table.find_one({'_id':aid}).get('paper')
        hxs = HtmlXPathSelector(response)
        essays = hxs.select('//tr[@class="cit-table item"]')
        next_url = hxs.select('//td[contains(@style,"text-align:right;")]')
        next_url = next_url[0]
        for essay in essays:
          essay_title = essay.select('td[@id="col-title"]').select('a[contains(@href,"citations")]/text()').extract()
          essay_others = essay.select('td[@id="col-title"]').select('span[@class="cit-gray"]/text()').extract()
          essay_citation = essay.select('td[@id="col-citedby"]').select('a[@class="cit-dark-link"]/text()').extract()
          ##############################
          essay_title = essay_title[0]
          
          if len(essay_citation) == 0:
            essay_citation = 0
          else:
            essay_citation = essay_citation[0]

          x = ''
          for i in essay_others:
            try:
              x = x + i
            except:
              pass
          essay_others = x
          #############################
          essay_history = [{'time':time.ctime(time.time()),'citation':essay_citation}]
          essay_info = {}
          if paperList == []:
            essay_info = {'title':essay_title,'citation':essay_citation,'essay_others':essay_others,'history':essay_history}

          else:
            for paper in paperList:
              if paper['title'] == essay_title:
                if 'history' in paper:
                  essay_history.extend(paper['history'])
                if 'pid_in_mysql' in paper:
                  essay_info = {'title':essay_title,'citation':essay_citation,'essay_others':essay_others,'history':essay_history,'pid_in_mysql':paper['pid_in_mysql']}
                else:
                  essay_info = {'title':essay_title,'citation':essay_citation,'essay_others':essay_others,'history':essay_history}
                paperList.remove(paper)              
                break
              else:
                essay_info = {'title':essay_title,'citation':essay_citation,'essay_others':essay_others,'history':essay_history}
          paperList.append(essay_info)
        self.table.update({'_id':aid},{"$set":{'paper':paperList}})
        next_url = next_url.select('a/@href').extract()
        if 'start' in response.meta:
          if len(next_url) == 1:
            next_url = next_url[0]
            if type(next_url) is not str:
              next_url = str(next_url)
          else:
            requests = self.start_next(pointer)
            if requests == []:
              print 'busy'
            else:
              for request in requests:
                yield request
                self.proxy_usetime+=1
                if self.proxy_usetime>3:
                  changep()
        else:
          if len(next_url) == 1:
            next_url = False
            print '%d %s procedure has been finished'%(aid,self.table.find_one({'_id':aid}).get('name'))
            requests = self.start_next(pointer)
            if requests == []:
              print 'busy'
            else:
              for request in requests:
                yield request
                self.proxy_usetime+=1
                if self.proxy_usetime>3:
                  self.changep()
          elif len(next_url) ==2:
            next_url = next_url[1]
            if type(next_url) is not str:
              next_url = str(next_url)
        if next_url:
          next_url = 'http://scholar.google.com.hk' + next_url
          request = Request(next_url,dont_filter = True,callback = self.parse, meta = {'dont_redirect':True,'dont_retry':True,'User-agent':random.choice(AGENTS),'aid':aid,'proxy':self.proxy,'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'cookie_jar': cookieJar,'pointer':pointer})
          yield request
          self.proxy_usetime+=1
          if self.proxy_usetime > 3:
            self.changep()
        else:
        	pass


    def aname(self,aid):
      self.cursor.execute("select names from na_person where id = %d"%aid)
      authorname = self.cursor.fetchall()
      if authorname == []:
        return self.aname(aid+1)
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
        self.table.insert({'_id':aid,'paper':[],'name':_list})

    def seperateName(self,name):
      nameList = name.split(',')
      return nameList

    def start_next(self,iid):
      '''
      generate requests by given aid
      return requests as a list. if name already exists in pubtable, return empty request list.
      '''
      pointer = iid
      if iid < 39591:
        pointer+=1
      else:
        print '*************************************************************'
        print 'PriorityPeople have been done'
        print '*************************************************************'
        pointer =0
      requests = []

      i = 0
      while i <= 3:
        _aid = PriorityPeople[pointer]
        account = False
        try:
          account = self.table_account.find_one({'_id':_aid}).get('account')
        except:
          account = False
        if account:
          if (pointer) not in self.crawlli:
            self.crawlli.append(pointer)
            authorname = self.aname(_aid)
            authornameList = self.seperateName(authorname)
            if self.table.find_one({'_id':_aid}) is None:
              self.initial(authorname,_aid,authornameList)
            else:
            	pass
            urls = self.table_account.find_one({'_id':_aid}).get('pages')
            if len(urls) >= 2 :
              del urls[0]
              for url in urls:
                url = 'http://scholar.google.com.hk' + url + '&view_op=list_works&pagesize=100'
                request = Request(url,dont_filter = True,callback = self.parse, meta = {'dont_redirect':True,'dont_retry':True,'User-agent':random.choice(AGENTS),'aid':_aid,'proxy':self.proxy,'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'pointer':pointer,'start':True})
                requests.append(request)
            i += 1
            pointer += 1
            continue
          else:
            pointer+=1
            i += 1
            continue
        else:
          pointer += 1
          continue
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
          print aid
          a += 1
          continue
        else:
          print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
          print 'start crawlling at %d'%a
          return a

    def changep(self):
      print 'changing proxy'
      socket.setdefaulttimeout(3.0)
      test_url = 'http://www.baidu.com'
      while True:
        try:
          proxy = random.choice(Proxypool)
          proxy =  'http://'+proxy
          print proxy
        except:
          continue
        try:
          start = time.time()
          f = urllib.urlopen(test_url,proxies={'http':proxy})
          f.close()
        except:
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
            break
          else:
            continue
