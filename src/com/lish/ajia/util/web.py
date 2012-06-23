# -*- coding: utf-8 -*-
'''
Created on Sep 15, 2009

@author: bogao
'''
from com.lish.ajia.proxy.proxy import ProxyMgr, ProxyModel
from com.lish.ajia.util import HTTPErrors, REQUEST_HEADER
from urllib2 import URLError, HTTPError
import simplejson
import sys
import threading
import time
import urllib2

class HtmlRetriever:
	'''Retrieve html from internet by url (optional via a proxy).
	'''

	__instance = None
	__proxy_instance = None

	@staticmethod
	def getInstance(use_proxy):
		if use_proxy == True:
			if HtmlRetriever.__proxy_instance is None:
				HtmlRetriever.__proxy_instance = HtmlRetriever(use_proxy=use_proxy)
			return HtmlRetriever.__proxy_instance
		else:
			if HtmlRetriever.__instance is None:
				HtmlRetriever.__instance = HtmlRetriever(use_proxy=use_proxy)
			return HtmlRetriever.__instance


	default_timeout = 20 #@todo: ??

	def __init__(self, use_proxy=False, validate_html_callback=None):
		self.use_debug_proxy = False

		self.proxy_mgr = None
		self.proxy_return_conn = None
		self.proxy_queue = None
		if use_proxy:
			self.proxy_mgr, self.proxy_return_conn, self.proxy_queue = ProxyMgr.getInstance()#todo new one

		self.default_proxy_handler = urllib2.ProxyHandler({})
		if(validate_html_callback):
			self.validate_html_callback = validate_html_callback
		else:
			self.validate_html_callback = self.default_validate_htmlsource

		# pause system / detect mode parameters

		# count
		self.bad_connection_count 		 	 = 0		# 记录所有连接的失败的次数
		self.last_bad_connection_count 	 	 = 0		# 上次Interval时的次数，由ManagerThread查看确定是否Pause
		self.success_connection_count 		 = 0		# 记录所有连接的失败的次数
		self.last_success_connection_count 	 = 0		# 上次Interval时的次数，由ManagerThread查看确定是否Pause
		self.detect_mode			 		 = False	# 进入检测状态，由ManagerThread设置
		self.detect_mode_lock		 		 = threading.Lock()
		self.detect_interval				 = 5		# Detect mode check interval
		self.detect_success_count 			 = 0		# Detect mode 时连续的成功访问次数
		self.detect_url = "http://scholar.google.com/scholar?hl=en&q=allintitle%3AUsing+application+feedback+in+differentiated+services+and+policies&btnG=Search"
														# 测试网页
		self.detect_count 					 = 0
#		self.proxy_pipe_lock				 = threading.Lock()
		self.proxy_return_pipe_lock			 = threading.Lock()

	def getPipeProxy(self): # TODO not block
		while True:
			proxy = self.proxy_queue.get(4)
			if proxy:
				return proxy
			else:
				print "error get proxy"

	def returnPipeProxy(self, proxy, action):
		with self.proxy_return_pipe_lock:
			if proxy is not None:
				self.proxy_return_conn.send([proxy.ip, proxy.port, action]) #ip, port, action


	#@return: Source Html of url. 
	def getHtmlRetry(self, url, retry=0, with_proxy=True):
		if retry <= 0: 
			retry = 5 
		html = None
		source = None
		retry_count = 0
		while retry > 0:
			retry -= 1
			retry_count += 1

			# detect mode
			self.wait_for_detect_mode()

			error_msg = None
			proxy = None
			try:
				if not with_proxy:
					print "Download [%s] without proxy" % url
					opener = urllib2.build_opener()
					opener.addheaders = [
										("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
										('User-agent', 'Mozilla/5.0'),
										("Accept-Language", "en-US,en;q=0.8"),
										("Cache-Control", "max-age=0"),
										("Connection", "keep-alive"),
										("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19")
										]
					html = opener.open(url)
					source = html.read()
					time.sleep(5)
				else:
					proxy_handler = self.default_proxy_handler
					if with_proxy and self.proxy_mgr is not None:
						proxy = self.getPipeProxy()
						if proxy:
							print "\t\t- use proxy(%s:%s)" % (proxy.ip, proxy.port)
						else:
							print '\t\t- proxy error'
							
						proxy_handler = urllib2.ProxyHandler({proxy.type :'http://%s:%s/' % (proxy.ip, proxy.port)})
	
					if self.use_debug_proxy:  # debug
						proxy_handler = urllib2.ProxyHandler({'http' :'http://keg:keg2007@166.111.68.67:3128/'})
	
					# download
					opener = urllib2.build_opener(proxy_handler)
					opener.addheaders = REQUEST_HEADER
					html = opener.open(url, timeout=HtmlRetriever.default_timeout)
					source = html.read()

			except HTTPError, e:
				error_msg = "Error [%s, %s]" % (e, "")
			except URLError, e:
				error_msg = "Error [%s, %s]" % (e.reason, "")
			except Exception, e:
#				print '-------------------------'
				error_msg = "Error [%s, %s]" % (sys.exc_info(), "")
#				import traceback
#				traceback.print_exc()
#				print '-------------------------'

			# on error
			if error_msg is not None:
				self.bad_connection_count += 1
				if with_proxy and self.proxy_mgr is not None:
					self.returnPipeProxy(proxy, "bad")
					if proxy is None: proxy = ProxyModel("-", "-", "-")
#					print "[X] Use Proxy %s:%s>%s, HtmlGetter err:%s, retry:%s." % \
#						(proxy.ip, proxy.port, proxy.value, error_msg, retry_count)
				else:
#					print "[X] HtmlGetter err:%s, retry:%s." % (error_msg, retry_count)
					pass

			if error_msg is None and self.validate_html(html) and self.validateBasicHTML(url, source) and self.validate_html_callback(source):
				self.success_connection_count += 1
				if with_proxy and self.proxy_mgr is not None:
					self.returnPipeProxy(proxy, "good")
					# print "[%s] Use Proxy %s:%s>%s" % (self.success_connection_count, proxy.ip, proxy.port, proxy.value)
				# print "[%s] success access webpage." % self.success_connection_count
				return source

		#End while

		if retry == 0:
			return None # meet max retry times. also None

		print "should not be here."
		return None

	def validateBasicHTML(self, url, source):
		if source is None or len(source.strip()) == 0:
			if True:
				print "## DEBUG: invalid page content:"
				print "## URL: ", url
				print "## html:", source, "<<<END Source" 
			return False
		return True
		
	## @deprecated: Not used yet.
	## @return: JSON of google ajax api. simplejson
	def getHTMLByGoogleAjax(self, url, retry=0, with_proxy=True):
		if retry <= 0: retry = 20 # default retry 20 times.
		html = None
		source = None
		retry_count = 0
		while retry > 0:
			retry -= 1
			retry_count += 1
			error_msg = None
			proxy = None
			try:
				proxy_handler = self.default_proxy_handler
				#@todo: use proxymgr
				if with_proxy and self.proxy_mgr is not None:
					proxy = self.getPipeProxy()

					if proxy: print "\t\t- use proxy(%s:%s)" % (proxy.ip, proxy.port)
					else: print '\t\t- proxy error'

					# format {'http': 'http://www.example.com:3128/'} ! http must be lowercase
					proxy_handler = urllib2.ProxyHandler({proxy.type :'http://%s:%s/' % (proxy.ip, proxy.port)})

				if self.use_debug_proxy:  # debug
					proxy_handler = urllib2.ProxyHandler({'http' :'http://keg:keg2007@166.111.68.67:3128/'})

				opener = urllib2.build_opener(proxy_handler)
				opener.addheaders = REQUEST_HEADER
				html = opener.open(url, timeout=HtmlRetriever.default_timeout)
				json_results = simplejson.load(html)
				
			except HTTPError, e:
				error_msg = "Error [%s, %s]" % (e, "")
			except URLError, e:
				error_msg = "Error [%s, %s]" % (e.reason, "")
			except Exception, e:
				error_msg = "Error [%s, %s]" % (sys.exc_info(), "")

			# on error
			if error_msg is not None:
				self.bad_connection_count += 1
				if with_proxy and self.proxy_mgr is not None:
					self.returnPipeProxy(proxy, "bad")
					if proxy is None: proxy = ProxyModel("-", "-", "-")
#					print "[X] Use Proxy %s:%s>%s, HtmlGetter err:%s, retry:%s." % \
#						(proxy.ip, proxy.port, proxy.value, error_msg, retry_count)
				else:
#					print "[X] HtmlGetter err:%s, retry:%s." % (error_msg, retry_count)
					pass

			if error_msg is None and self.validate_google_json(json_results):
				self.success_connection_count += 1
				if with_proxy and self.proxy_mgr is not None:
					self.returnPipeProxy(proxy, "good")
					#print "[%s] Use Proxy %s:%s>%s" % (self.success_connection_count, proxy.ip, proxy.port, proxy.value)
				#print "[%s] success access webpage." % self.success_connection_count
				
				return json_results

		#~ end while

		if retry == 0:
			return None # meet max retry times. also None

		print "should not be here."
		return None

	#
	# Validators
	#
	def validate_html(self, html):
		if html is None:
			return False
		if html.code in HTTPErrors:
			print "error found: %s: %s " % HTTPErrors[html.code]
			return False
		else:
			return True;
		
	def validate_google_json(self, json_result):
		if json_result is None : return False
		if json_result['responseStatus'] in HTTPErrors:
			print "error found: %s: %s " % HTTPErrors[json_result['responseStatus']]
			return False
		else:
			return True;

	def enter_detect_mode(self):
		self.detect_success_count = 0
		self.detect_mode = True

	def leave_detect_mode(self):
		self.detect_mode = False

	def wait_for_detect_mode(self):
		if not self.detect_mode: return 		# escape
		with self.detect_mode_lock:				# detect thread. only one thread can run here.
			if not self.detect_mode: return 	# escape again

			print "=================================================================="
			print "= Network may has some problem, or banned. Switch in DETECT MODE ="
			print "=================================================================="

			while self.detect_mode:	# check again
				self.detect_count += 1
				# detect.
				html = None
				try:
					opener = urllib2.build_opener(self.default_proxy_handler)
					opener.addheaders = self.request_header
					html = opener.open(self.detect_url, timeout=HtmlRetriever.default_timeout)
				except:
					print "Detect(%s): HtmlGetter Error %s" % (self.detect_count, sys.exc_info()[0])
					self.detect_success_count -= 2
					if self.detect_success_count < 0:
						self.detect_success_count = 0

				if html is not None:
					print "Detect(%s): Good Connection %s." % (self.detect_count, self.detect_success_count)
					self.detect_success_count += 1

				time.sleep(self.detect_interval)

			print "\n= Leave DETECT MODE =\n"
			self.detect_success_count = 0
			self.detect_count = 0

	#
	# Callbacks
	#
	def default_validate_htmlsource(self, source):
		'''Callback methods, return false if the html returned is not valid.
		'''
		# if not source or len(source) == 0:
		# return False
		# print "validate html" + html
		return True


def doit(getter, url):
	getter.getHtmlRetry(url, 2, True)


#\_________________________
# Test
###########################

def test_proxyget(url, retry=0, with_proxy=True):
	#proxy_handler = urllib2.ProxyHandler({'http' :'http://%s:%s/' % ('166.111.68.67', '3128')})
	#proxy_handler = urllib2.ProxyHandler({})
	# download
	opener = urllib2.build_opener()
	opener.addheaders = REQUEST_HEADER
	html = opener.open(url, timeout=HtmlRetriever.default_timeout)

	source = html.read()
	return source

if __name__ == '__main__':
#	html = test_proxyget('http://www.google.com')
	html = test_proxyget('http://scholar.google.com/scholar?hl=en&num=100&q=%22A%20fast%20algorithm%20for%20computing%20distance%20spectrum%20of%20convolutional%20codes.%22OR%22A%20new%20upper%20bound%20on%20the%20first-event%20error%20probability%20for%20maximum-likelihood%20decoding%20of%20fixed%20binary%20convolutional%20codes.%22')
	print html[0:1000], "..."
	

