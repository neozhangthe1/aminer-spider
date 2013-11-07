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

class testspider(BaseSpider):
	name = 'testspider'
	start_urls=['http://scholar.google.com.hk/scholar?q=Using+graphical+tools+in+a+phased+activity+for+enhanc%20ing+dialogical+skills:+An+example+with+Digalo.&hl=en&num=20&as_sdt=0%2C5&as_ylo=%202004&as_yhi=2010']
	def parse(self,response):
		hxs = HtmlXPathSelector(response)
		essays = hxs.select('//div[@class="gs_r"]').select('div[@class="gs_ri"]')
		for essay in essays:
			try:
				title2 = essay.select('h3[@class="gs_rt"]').select('a').extract()
				title2=title2[0].split('target="_blank">')
				del title2[0]
				title = ''
				for part in  title2:
					_part = part.replace('<b>','')
					_part = _part.replace('</b>','')
					_part = _part.replace('</a>','')
					title = title + _part
				print title
				print len(title)
			except:
				continue