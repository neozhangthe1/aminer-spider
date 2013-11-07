import os
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'project.settings') 


from scrapy import log, signals, project
from scrapy.xlib.pydispatch import dispatcher
import settings
from scrapy.crawler import CrawlerProcess
from multiprocessing import Process, Queue
from spiders.titlespider import Titlespider
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
#from tutorial.items import EssayInfo
#from tutorial.agents import AGENTS
#from tutorial.proxy import PROXIES
from scrapy.http.cookies import CookieJar

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


class CrawlerScript():
	def __init__(self):
		self.crawler = CrawlerProcess(settings)
		#if not hasattr(project, 'crawler'):
			#self.crawler.install()
		#self.crawler.configure()
		self.items = []
		dispatcher.connect(self._item_passed, signals.item_passed)

	def _item_passed(self, item):
		self.items.append(item)

	def _crawl(self, queue, spider_name):
		spider = self.crawler.spiders.create(spider_name)
		if spider:
			self.crawler.queue.append_spider(spider)
			self.crawler.start()
			self.crawler.stop()
			queue.put(self.items)
	def crawl(self, spider):
		queue = Queue()
		p = Process(target=self._crawl, args=(queue, spider,))
		p.start()
		p.join()
		return queue.get(True)

if __name__ == "__main__":
	log.start()
	items = list()
	crawler = CrawlerScript()

	for i in range(3):
		items.append(crawler.crawl(Titlespider))
	print items