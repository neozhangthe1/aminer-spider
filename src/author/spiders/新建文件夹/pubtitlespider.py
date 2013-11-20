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
import editdist

class pubtitlespider(BaseSpider):
    name = 'pubtitlespider'
    conn = pymongo.Connection(host='10.1.1.111',port=12345)
    #conn = pymongo.Connection(host='166.111.134.53',port=12345)
    db = conn['arnet_db']
    table = db['publication_test']
    error = db['errorlist1']
    dproxy = db['prorxy']
    #connect to the mongo database, adaptable when needed
    conn_my = MySQLdb.connect(host="arnetminer.org",user="root",passwd="eserver4009",db="arnet_db")
    #conn_my = MySQLdb.connect(host="166.111.134.53",user="root",passwd="keg2012",db="arnet_db")
    cursor = conn_my.cursor()
    #connect to the MySQL database, adaptable when needed
    def __init__(self):
        self.proxy=''
        self.a = buildPP()
        self.pp = self.a.getpp(3)
        self.ppointer = self.getppointer()
        self.proxy_usetime = 0
        self.changep()
        self.pointer = self.startpointer()-1
        self.begin = True
        self.requestpool = []
        self.genewrequest()        

    def start_requests(self):
        requests = []
        for i in range(3):
            requests.append(self.nextrequest())
        for request in requests:
            yield request

    def parse(self,response):
      cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
      cookieJar.extract_cookies(response, response.request)
      this_title=response.meta['title']
      aid = response.meta['aid']
      pid = response.meta['pid']
      if response.status !=200:
        if response.meta['proxy'] == self.proxy:
          self.changep()      
        request = Request(response.url, dont_filter = True,callback = self.parse, meta = {'dont_redirect':True,'dont_retry':True,'User-agent':random.choice(AGENTS),'aid':self.pointer,'proxy':self.proxy,'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'pid':pid,'title':this_title})
        cookieJar.add_cookie_header(request) # apply Set-Cookie ourselves
        yield request
      if response.status ==200 :        
        print 'successfully'
        hxs = HtmlXPathSelector(response)
        paperList = self.table.find_one({'_id':aid}).get('paper')
        essays = hxs.select('//div[@class="gs_r"]').select('div[@class="gs_ri"]')#extract classes of html information
        essay_info = {'title':this_title,'pid_in_mysql':pid}
        for essay in essays:
           essay_citation = essay.select('div[@class="gs_fl"]').select('a[contains(@href,"cites")]/text()').extract()
           essay_title = essay.select('h3[@class="gs_rt"]').select('a/text()').extract()
           essay_others = essay.select('div[@class="gs_a"]').select('a/text()').extract()
           if essay_citation == []:
            essay_citation = 0
           else:
            essay_citation = essay_citation[0]
            essay_citation = essay_citation[9:]
            essay_citation = int(essay_citation)
         
           if essay_title == []:
            continue
            if type(essay_title[0]) is not str:
              continue
           else:
            essay_title = self.extracttitle(essay.select('h3[@class="gs_rt"]').select('a').extract())
           if essay_others == []:
            essay_others = essay.select('div[@class="gs_a"]')[0].extract()
            if essay_others is None:
              essay_others = ''
            else: 
              x = ''
              if type(essay_others) is list:
                for i in essay_others:
                  if type(i) is list:
                    for _i in i:
                      x = x + _i
                  if type(i) is str:
                    x = x + i
              essay_others = essay_others.lstrip('<div class="gs_a">')
              essay_others = essay_others.rstrip('</div>')
              essay_others = re.sub("(<(.*?)>)", "", essay_others)
           if self.matchtitle(essay_title,this_title):
             print '!!!!!!!!!!!!!!!!!'    
             essay_info = {'title':essay_title,'citation':essay_citation,'essay_others':essay_others,'pid_in_mysql':pid}
             paperList.append(essay_info)
             self.table.update({'_id':aid},{"$set":{'paper':paperList}})
             break
           else:
            print essay_title
            print this_title
            print 'no matched'



        request = self.nextrequest()
        yield request

    def findpublication8name(self,aid):

        '''
        returns a list like:[['title1','title2'],id]
        '''
        
        cursor_my = self.conn_my.cursor()#mysql cursor

        if type(aid) is not list:
            cursor_my.execute('select pid from na_author2pub where aid = "%s"'%aid)
            pid = cursor_my.fetchall()
            pidList=[]
            for perid in pid:
                pidList.append(perid[0])

        else:
            pass
        paperList=[]
        for perid in pid:
            cursor_my.execute('select title,year from publication where id = %d'%perid)
            info = cursor_my.fetchall()
            info = info[0]
            title = info[0]
            year = info[1]
            paperList.append({'title':title,'year':year})        
        items=[]
        count = 0
        
        for paper in paperList:
            item={'title':paper['title'],'pid':pid[count],'year':paper['year']}
            count += 1
            items.append(item)
        return items
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
    def matchtitle(self,gtitle,mtitle):

        short_key = mtitle.lower()
        key_title = gtitle.lower()
          
        exactmatched = False                             

        if short_key==key_title:
            exactmatched = True
        if not exactmatched:#if can not be critical matched, try by calculate Levenshtein distance
            x = ''
            y = ''
            for ch in short_key:
              if ch<=chr(127):
                x = x+ch
            for ch in key_title:
              if ch<=chr(127):
                y = y+ch
            short_key = x
            key_title = y
            ed = editdist.distance(short_key,key_title)
            print ed                    
            if ed < 15:#adaptable
              exactmatched = True

        return exactmatched
    def cleanGoogleTitle(self,title):
        '''
        return a list containing 3 element
        '''
        has_dot = False
        titleCleaned = title
        

        # clean step 1
        titleCleaned = re.sub("(<(.*?)>)", "", titleCleaned)
        # if has dot
        re_hasdot = re.compile(".", re.I)
        match = re_hasdot.search(title)
        if match is not None:
            has_dot = True
        # clean step 2, here title is readable
        titleCleaned = re.sub("(&nbsp;|&#x25ba;|&hellip;)", "", titleCleaned)
        titleCleaned = re.sub("(&#.+?;|&.+?;)", "", titleCleaned)
        titleCleaned = titleCleaned.strip()
        readableTitle = titleCleaned

        # Shrink, only letters left
        titleCleaned = re.sub("\W", "", titleCleaned)
        titleCleaned = titleCleaned.lower()
        return (readableTitle, titleCleaned, has_dot)
    def nextrequest(self):
        if self.requestpool != []:
            request = self.requestpool[0]
            del self.requestpool[0]
            return request
        elif self.requestpool ==[]:
            requests = self.genewrequest()
            for request in requests:
                self.requestpool.append(request)
            return self.nextrequest()
    def genewrequest(self):
        while True:
          self.pointer += 1
          if self.pointer in PriorityPeople:
            print self.pointer,'is PriorityPeople'
            continue
          else:
            pubs = self.findpublication8name(self.pointer)
            self.initial(self.pointer)
            if len(pubs) == 0:
                print 'no pub'            
                continue
            else:

              print 'adding requests'
              requests = []
              for pub in pubs:
                title = pub['title']
                year = pub['year']
                y1 = year -3
                y2 = year +3
                pid = pub['pid']
                url = 'http://scholar.google.com.hk/scholar?q=%s&hl=en&num=20&as_sdt=0%%2C5&as_ylo=%d&as_yhi=%d'%(title.replace(' ','+'),y1,y2)
                request = Request(url, dont_filter = True,callback = self.parse, meta = {'proxy':self.proxy,'dont_redirect':True,'dont_retry':True,'User-agent':random.choice(AGENTS),'aid':self.pointer,'handle_httpstatus_list':[302,503,200,307,403,404,502,500,504],'pid':pid,'title':title})
                requests.append(request)
              break

        return requests
                
    def initial(self,aid):
        self.cursor.execute('select names from na_person where id =%d'%aid)
        name = self.cursor.fetchall()
        while type(name) is list or type (name) is tuple:
          name = name[0]
        check = 0
        _list = ''
        for i in name:
          if i <= chr(127):
            _list = _list + i
        print _list
        self.table.insert({'_id':aid,'name':_list,'paper':[]})
    def startpointer(self):
        a = 0
        while True:
            if a not in PriorityPeople:
                if self.table.find_one({'_id':a}) is None:
                    print 'start at ',a
                    return a
                    break
                else:
                    a += 1
                    continue
            else:
                a+=1
                continue
    def extracttitle(self,title2):
      try:
        title2 = title2[0].split('target="_blank">')
        del title2[0]
        title = ''
        for part in title2:
          _part = part.replace('<b>','')
          _part = _part.replace('</b>','')
          _part = _part.replace('</a>','')
          title = title + _part
          return title
      except:
        return ''