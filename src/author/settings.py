# Scrapy settings for tutorial project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import random
from author.agents import AGENTS
import middleware
from author.rotate_useragent import RotateUserAgentMiddleware
from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from author.spiders import extractor
BOT_NAME = 'author'

SPIDER_MODULES = ['author.spiders']
NEWSPIDER_MODULE = 'author.spiders'
AUTOTHROTTLE_ENABLED = True
COOKIES_DEBUG = True
DOWNLOAD_DELAY = 0.25
#CLOSESPIDER_PAGECOUNT = 150
COOKIES_ENABLED = False
#DUPEFILTER_CLASS = False


DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware' : None,
    'author.middleware.CustomHttpProxyMiddleware': 100,
    'author.rotate_useragent.RotateUserAgentMiddleware' :400,

}



#DefaultHeadersMiddleware = {'User-agent':random.choice(AGENTS)}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tutorial (+http://www.yourdomain.com)'
