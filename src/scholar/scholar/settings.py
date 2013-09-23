# Scrapy settings for scholar project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'Mozilla'
BOT_VERSION = '5.0 (X11; Linux x86_64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1'

DOWNLOAD_DELAY = 2 #this is to reduce the chance of blocking by google

SPIDER_MODULES = ['scholar.spiders']
NEWSPIDER_MODULE = 'scholar.spiders'
DEFAULT_ITEM_CLASS = 'scholar.items.ScholarItem'
DEFAULT_RESPONSE_ENCODING = "utf-8"
ITEM_PIPELINES=['scholar.pipelines.ScholarPipeline','scholar.pipelines.MongoDBPipeline',]
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

# FEED Configuration

#FEED_URI = 'file:///tmp/refs.json'
#FEED_FORMAT = 'jsonlines'

# MongoDB configuration

MONGO_DATABASE = "Scholar"
