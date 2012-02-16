# -*- coding: utf-8 -*-
'''
'''
from com.lish.ajia.googlescholar.settings import Settings
from com.lish.ajia.proxy.models import *
from com.lish.ajia.util.webstatic import WebPageDownloader
import os
import re
import time

class ProxyLoader():

	# Group(1) = 216.239.59.83 #Group(2) = 80 #Group(3) = HTTP #Group(4) = 美国/加拿大 ProxyCN #Group(5) = 06-07 22:06

	def __init__(self, manager_instance, load_from_web=False):
		self.settings = Settings.getInstance()
		self.proxyResource = ProxyResource()
		self.manager = manager_instance
		self.html_getter = WebPageDownloader();
		self.filename = os.path.join(self.settings.resourcedir, "proxies.txt")
		self.filename_static = os.path.join(self.settings.resourcedir, "proxies_static.txt")

		self.autosave_interval = (5, 12 * 5) # (seconds * check times)
		self.autosave_checkcount = 0

		# load first
		if os.path.exists(self.filename) and not load_from_web:
			self.loadFromFile()

		if len(self.manager.proxies) < 10:
			print "Load too less proxies from file."
			self.loadProxyFromWeb()
			self.saveToFile()

		# unpaused to unblock getProxy.
		# self.manager.unpause()
		# print "pause set to false"

		# start auto_save thread
		# t_autosave = Thread(target=self.t_auto_save)
		# t_autosave.start()

	def t_auto_save(self):
		if self.manager.print_report:
			print 'start auto save'
		time.sleep(self.autosave_interval[0] * self.autosave_interval[1])
		while self.manager.daemon_running:
			if self.manager.print_report:
				print 'check auto save'
			if self.autosave_checkcount >= self.autosave_checkcount[1]:
				print "save proxy file"
				self.autosave_checkcount[1] = 0
				self.saveToFile()
			else:
				self.autosave_checkcount[1] += 1
			time.sleep(self.autosave_interval[0])

		print "proxy autosave thread finished."

	def loadFromFile(self):
		p_line = re.compile("([\\d.]*):(\\d+)\\t(\\w+)?\\t(\\w+)?\\t(.+)?\\t?(.+)?")
		#Group(1) = 221.215.72.218 Group(2) = 8080 Group(3) = HTTP Group(4)=type
		#Group(5) = 山东省 网通 Group(6) = 09-23 12:47

		# read from file
		f = file(self.filename, "r")
		try:
			contents = f.read()
			matches = p_line.findall(contents)
			if matches is not None:
				for result in matches:
					#Group(1) = 216.239.59.83 
					#Group(2) = 80 
					#Group(3) = HTTP
					#Group(4) = value
					#Group(5) = 美国/加拿大 ProxyCN
					#Group(6) = 06-07 22:06
					ip = result[0]
					port = result[1]

					if ip in self.manager.proxies:
						continue

					model = ProxyModel(ip, port, result[2].strip().lower())
					model.value = int(result[3])
					model.location = result[4]
					model.validate_date = result[5]
					self.manager.proxies[ip] = model
					self.manager.proxyQueue.put(ProxyKey(ip, model.value))
			print "load %s proxies from %s." % (len(self.manager.proxies), self.filename)

		except:
			print "Load proxies from file error."
		f.close()

		# load static

		# read from file
		f = file(self.filename_static, "r")
		try:
			contents = f.read()
			matches = p_line.findall(contents)
			if matches is not None:
				for result in matches:
					#Group(1) = 216.239.59.83 
					#Group(2) = 80 
					#Group(3) = HTTP
					#Group(4) = value
					#Group(5) = 美国/加拿大 ProxyCN
					#Group(6) = 06-07 22:06
					ip = result[0]
					port = result[1]
					if ip in self.manager.proxies:
						continue

					model = ProxyModel(ip, port, result[2].strip().lower())
					model.value = int(result[3])
					model.location = result[4]
					model.validate_date = result[5]
					self.manager.proxies[ip] = model
					self.manager.proxyQueue.put(ProxyKey(ip, model.value))
			print "load %s proxies from %s." % (len(self.manager.proxies), self.filename_static)
		except:
			print "Load proxies from file error."
		f.close()

		print "Load %s proxies." % len(self.manager.proxies)

	#
	# Load & Save
	# 
	def saveToFile(self):
		file_abspath = self.filename
		if os.path.exists(file_abspath):
			os.remove(file_abspath)
			print "$proxy/> remove %s." % file_abspath

		# write to file
		f = file(file_abspath, "w")
		for proxyModel in self.manager.proxies.itervalues():
			f.write(proxyModel.to_line())
			f.write("\n")

		#@todo: And sleepQueue.

		f.close()
		print "$proxy/> write proxies to %s." % f.name

	def loadProxyFromWeb(self):
		proxies = ProxyResource().load_proxycn()
		for proxy in proxies:
			self.manager.proxies[proxy.ip] = proxy
			self.manager.proxyQueue.put(ProxyKey(proxy.ip, 50))



class ProxyResource:
	def __init__(self):
		self.settings = Settings.getInstance()
		self.html_getter = WebPageDownloader();
		# self.filename = os.path.join(self.settings.resourcedir, "proxies.txt")

	def load_proxycn(self):
		'''
		'''
		# class resource
		psource_template = "http://www.proxycn.cn/html_proxy/port%s-%s.html"
		psource_ports = (8080, 80, 81, 3128, 8000, 1080, 444)
		p_nextpage = re.compile("<a href=[^>]*>下一页</a>")
		p_proxy = re.compile("<TR [^>]* onDblClick=\"clip\\('([\\d.]+):(\\d+)'\\);alert\\('已拷贝到剪贴板!'\\)[^\\x00]+?<TD class=\"list\">\\d+</TD><TD class=\"list\">(\\w*)</TD><TD class=\"list\">([^<]*)</TD><TD class=\"list\">([^<]*)</TD>")

		# another place
		proxy_urls = []
		proxy_urls.append("http://www.cnproxy.com/proxy1.html");
		proxy_urls.append("http://www.cnproxy.com/proxy2.html");
		proxy_urls.append("http://www.cnproxy.com/proxy3.html");
		proxy_urls.append("http://www.cnproxy.com/proxy4.html");
		proxy_urls.append("http://www.cnproxy.com/proxy5.html");
		proxy_urls.append("http://www.cnproxy.com/proxy6.html");
		proxy_urls.append("http://www.cnproxy.com/proxy7.html");
		proxy_urls.append("http://www.cnproxy.com/proxy8.html");
		proxy_urls.append("http://www.cnproxy.com/proxy9.html");
		proxy_urls.append("http://www.cnproxy.com/proxy10.html");
		p_proxy2 = re.compile("<tr><td>(\\d+\\.\\d+\\.\\d+\\.\\d+)<SCRIPT type=text/javascript>[^<]+?</SCRIPT></td><td>(.+?)</td><td>")

		proxies = []
		for port in psource_ports:
			page = 0
			hasNext = True
			while hasNext:
				page += 1
				purl = psource_template % (port, page)
				hasNext = self.__loadProxyFromURL(proxies, purl, p_proxy)
		# load from 2 place
		#		for url in proxy_urls:
		#			self.__loadProxyFromURL2(url, p_proxy2)

		return proxies

	def load_proxyServer(self):
		proxies = []
		url = "http://www.proxynova.com/get_proxies.php?proxy_type=2&btn_submit=Download+all+Proxies"
		self.__loadFromProxyServer(proxies, url)
		return proxies


	def __loadFromProxyServer(self,proxies,url):
		print "load proxies from %s " % url
		source = self.html_getter.getHtmlRetry(url,3)
		source = unicode(source, "UTF-8").encode("UTF-8")
		print source		
		results = source.split("\n")[2:-2]
		count = 0
		if results is not None:
			for x in results:
				result = x.split(":")
				print "hi "+x
				ip = result[0]
				port = result[1]
				print "length:%s ip:%s  port:%s " % (len(result),ip,port)		
				model = ProxyModel(ip,port,"proxyServer")
				proxies.append(model)
				count += 1
		print "---proxyLoader---:load proxy from proxyServer get %s " % count
		
	def __loadProxyFromURL(self, proxies, url, pattern):
		'''Put model into ProxyModel, return has_next_page.'''

		p_nextpage = re.compile("<a href=[^>]*>下一页</a>")  # copy

		print "---proxyloader---:load proxy from %s" % url
		source = self.html_getter.getHtmlRetry(url, 3)
		source = unicode(source, "gbk").encode("UTF-8")
		foundNextPage = p_nextpage.search(source)

		results = pattern.findall(source)
		count = 0
		if results is not None:
			for result in results:
				ip = result[0]
				port = result[1]

				model = ProxyModel(ip, port, result[2].strip().lower())
				model.location = result[3]
				model.validate_date = result[4]
				proxies.append(model)
				count += 1
		print "---proxyloader---:load proxy from %s (get %s)" % (url, count)
		return foundNextPage


	def saveToFile(self, file_abspath, proxies):
		'''Save list of ProxyModel in a file.'''
		if os.path.exists(file_abspath):
			os.remove(file_abspath)
			print "$proxy/> remove %s." % file_abspath

		# write to file
		f = file(file_abspath, "w")
		for proxyModel in proxies:
			f.write(proxyModel.to_line())
			f.write("\n")
		f.close()
		print "$proxy/> write proxies to %s." % f.name

def test_load_proxycn():
	proxyRes = ProxyResource()
	results = proxyRes.load_proxycn()
	for model in results:
		print model
	proxyRes.saveToFile('/tmp/proxies.text', results);

def test_load_5uproxy_net():
	proxyRes = ProxyResource()
	results = proxyRes.load_proxycn()
	for model in results:
		print model
	proxyRes.saveToFile('/tmp/proxies.text', results);

if __name__ == '__main__':
#	test_load_proxycn()
	test_load_5uproxy_net()
	print "load done."

