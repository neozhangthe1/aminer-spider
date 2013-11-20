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
class test(BaseSpider):
    name = 'test'
    #allowed_domains = ['scholar.google.com']
    start_urls=['http://scholar.google.com.hk/scholar?start=1000&q=jie+tang&hl=en&as_sdt=0,5']
    #http://scholar.google.com.hk/citations?hl=en&user=UedS9LQAAAAJ&pagesize=100&view_op=list_works&cstart=2900
    def parse(self,response):
      hxs = HtmlXPathSelector(response)
      url = hxs.select('//td[contains(@align,"left")]').select('a/@href').extract()
      print url
      


