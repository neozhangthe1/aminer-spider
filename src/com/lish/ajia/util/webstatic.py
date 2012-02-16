# -*- coding: utf-8 -*-
from com.lish.ajia.util import HTTPErrors, REQUEST_HEADER
from urllib2 import URLError, HTTPError
import sys
import urllib2

class WebPageDownloader:
	'''Retrieve html from internet by url (optional via a proxy).'''


	def __init__(self):
		self.default_timeout = 40

	#@return: Source Html of url. 
	def getHtmlRetry(self, url, retry=0):
		if retry <= 0: retry = 20 # default retry 20 times.
		html = None
		source = None
		retry_count = 0
		while retry > 0:
			retry -= 1
			retry_count += 1

			error_msg = None
			try:
				proxy_handler = urllib2.ProxyHandler({})
				opener = urllib2.build_opener(proxy_handler)
				opener.addheaders = REQUEST_HEADER
				html = opener.open(url)
				source = html.read()
			except HTTPError, e:
				error_msg = "Error [%s, %s]" % (e, "")
			except URLError, e:
				error_msg = "Error [%s, %s]" % (e.reason, "")
			except:
				error_msg = "Error [%s, %s]" % (sys.exc_info(), "")

			# on error
			if error_msg is not None:
				print "[X] HtmlGetter err:%s, retry:%s." % (error_msg, retry_count)

			if error_msg is None and self.validate_html(html):
				print "[v] success access webpage."
				return source

		#~ end while

		if retry == 0:
			return None # meet max retry times. also None
		print "should not be here."
		return None

	#
	# Validators
	#
	def validate_html(self, html):
		if html is None : return False
		if html.code in HTTPErrors:
			print "error found: %s: %s " % HTTPErrors[html.code]
			return False
		else:
			return True;

#\_________________________
# Test
###########################
if __name__ == '__main__':
	print WebPageDownloader().getHtmlRetry('http://www.google.com', 1)



