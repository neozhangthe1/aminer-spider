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


class extractor(BaseSpider):
    name = 'extractor'
    


    def __init__(self):
      self.pages = 1

      self.start_urls = ["http://simpleproxylist.com/search.php?country=any&state=any&type=http&security=any&ssl=any&scrapebox=any&akismet=any&reliability=90"]
      self.fw = open(r'C:\Python27\author\author\extraproxies.txt','w')
      self.fw.close()

      
    def parse(self,response):
      fr = open(r'C:\Python27\author\author\extraproxies.txt','r')
      hxs=HtmlXPathSelector(response)
      proxies = []
      for i in fr.readlines():
        proxies.append(i)
      fr.close()
      fw = open(r'C:\Python27\author\author\extraproxies.txt','w')
      end = False
      if len(hxs.select('//p[@class="postmetadata"]/a').extract()) == 3 and self.pages !=1:
        end = True
      else:
        end = False
      tr = hxs.select('//tr')
      for proxy in tr:
        part1 = proxy.select('td[@valign="top"]/a/text()').extract()
        part2 = proxy.select('td[@valign="top"]/text()').extract()
        if len(part1) == 0 or len(part2) ==0:
          continue
        else:
          if part1[0].find('x') != -1:
            continue
          else:
            p = part1[0] + ':' + part2[0]+'\n'
            if p not in Proxypool:
              proxies.append(p)
      for proxy in proxies:
        fw.write(proxy)
      fw.close()
      if not end:
        self.pages+=1
        request = Request('http://simpleproxylist.com/search.php?p=%d&country=CN&state=any&type=http&security=any&ssl=any&scrapebox=any&akismet=any&reliability=any'%self.pages,callback=self.parse)
        yield request



      






