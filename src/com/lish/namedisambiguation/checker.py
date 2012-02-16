#!/usr/bin/env python
# -*- coding: utf-8 -*-
from com.lish.ajia.util.web import HtmlRetriever
from com.lish.namedisambiguation import EXCLUDE_NOISE_SITE
from com.lish.namedisambiguation.models import NAResult
from com.lish.namedisambiguation.parsegoogle import GoogleResultParser
from com.lish.namedisambiguation.settings import Settings
import threading
import time

class checker():
	def __init__(self):
		self.debug_print = True
		self.settings = Settings.getInstance()
		self.htmlRetriever = HtmlRetriever.getInstance(self.settings.use_proxy)
		self.htmlRetriever.validate_html_callback = self.validate_html_callback 
		self.parsegoogle = GoogleResultParser()
		
	def validate_html_callback(self, source):
		if source is None or len(source) < 100:
			return False
		
		#Web Images Videos Maps Finance
		if 'Web' in source and 'Images' in source and 'Finance' in source:
			return True
		else:
			print '---------------------'
			print 'SOURCE:\n'
			print source
			print '---------------------'
			return False
		
	def pinQuery(self, title1, title2):
		query = "".join(('"', title1, '" AND "', title2 , '"'))
		url = self.settings.urltemplate % query
		url = url.replace(" ", "%20").replace("\"", "%22")
		return url

	def isInSamePage(self, title1, title2, withProxy=False):
		'''Return NAResult
		'''
		url = self.pinQuery(title1, title2)
		print '> check url:', url
		
		html = None
		while html is None:
			html = self.htmlRetriever.getHtmlRetry(url, 10, withProxy)
#		print "************"
#		print html
#		print "************"
		found_urls = self.parsegoogle.extract_from_source(html)
		
		result = NAResult()
		
		final_found = False
		for found_url in found_urls:
#			print '>>>>>link:', found_url
			if len(found_url) >= 1:
				found, domain = self.foundInSamePage(found_url[1])
				if found:
					print '+ found domain: %s (%s)' % (domain, found_url)
					result.links.append(found_url[0]);
					final_found = True
				else:
					print '- found domain:%s (%s)' % (domain, found_url)
		result.result = final_found
		return result

			
	def isInSamePageMulti(self, title_pairs):
		''' Multithread check google method.
		'''
		isSameMatrix = {}
		threads = []
		
		i = 0
		for title1, title2 in title_pairs:
			threads.append(CheckGoogleThread(self, isSameMatrix, i, title1, title2))
			threads[i].start()
			i += 1
			time.sleep(0.2)

		restarted_threads = 0;
		restart_times = 10
		check_count = 0
		while True:
			alldone = True
			print ">> ", isSameMatrix
			for i in range(0, len(title_pairs) - 1):
				if i not in isSameMatrix:
					alldone = False
					if check_count % restart_times == 0 and restarted_threads < 3:
						threads[i] = CheckGoogleThread(self, isSameMatrix, i, title1, title2)
						threads[i].start()
						restarted_threads += 1
				
			if alldone and len(title_pairs) == len(isSameMatrix):
				print "All Done: ", isSameMatrix
				break
			time.sleep(2);
			
			check_count += 1
		
		# return	
		print '-' * 100
		print "-Return: ", isSameMatrix
		print '-' * 100
		return isSameMatrix
		

	def foundInSamePage(self, url):
		idx = url.find("/");
		domain = ''
		if idx > 0:
			domain = url[0:idx]
		else:
			domain = url
			
		if 'dblp' in url:
			return False, domain
		
		for excluded in EXCLUDE_NOISE_SITE:
#			print 'check with ', excluded,'--', domain
			if domain == excluded or domain.endswith(excluded) or excluded.endswith(domain):
				return False, domain
		return True, domain


#
# Thread Implementation of .....
#
class CheckGoogleThread(threading.Thread):
	''' Thread Implementation of processing Person
	'''

	def __init__(self, checker, isSameMatrix, i, title1, title2):
		threading.Thread.__init__(self)
		self.checker = checker
		self.isSameMatrix = isSameMatrix
		self.i = i
		self.title1 = title1
		self.title2 = title2
		print "+ Start thread ", i

	def run(self):
		try:
			# check done
			if self.i in self.isSameMatrix:
				return
			
			naResult = self.checker.isInSamePage(self.title1, self.title2, True);
			if self.i not in self.isSameMatrix:
				self.isSameMatrix[self.i] = naResult
			else:
				print "I am a very slow thread", self.i
				
			print "*** Update Boolean [%s] = %s " % (self.i, naResult.result) 
		except Exception, e:
			print '----------------------'
			print "Unexpected error:", e
			import traceback
			traceback.print_exc()
			print '----------------------'

		print "***********************************"
		print "$thread/%s:> Stopped." % self.i
		print "***********************************"



if __name__ == '__main__':
#	titles = []
	title1 = 'Asymptotic inference for spatial CDFs over time'
	title2 = 'Comparison of spatial variables over subregions using a block bootstrap. Journal of Agricultural, Biological, and Environmental Statistics'
	
#	titles.append([title1, title2])
#	titles.append([title1, title2])
#	t1 = "New event detection based on indexing-tree and named entity" 
#	t2 = "Term Committee Based Event Identification within News Topics"
	t1 = "System integrity revisited" 
	t2 = "Risks to the public in computers and related systems"
	checker = checker();
	print checker.isInSamePage(t1, t2, False)
#	print checker.foundInSamePage('pubzone.org/viewperson.do?id=-1&amp;name=william%20kent');
#	print checker.foundInSamePage('arnetminer.org/viewperson.do?id=-1&amp;name=william%20kent');
#	print checker.foundInSamePage('www.iminer.org/viewperson.do?id=38009&amp;name...');
	
#	found, domain = checker.foundInSamePage("www.informatik.uni-trier.de/~ley/db/indices/a.../Zhang:Kuo.html")
#	print found, domain
