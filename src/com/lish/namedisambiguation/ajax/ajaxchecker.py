#!/usr/bin/env python
# -*- coding: utf-8 -*-
from com.lish.ajia.util.web import HtmlRetriever
from com.lish.namedisambiguation import EXCLUDE_NOISE_SITE
from com.lish.namedisambiguation.parsegoogle import GoogleResultParser
from com.lish.namedisambiguation.settings import Settings

class checker():
	def __init__(self):
		self.debug_print = True
		self.settings = Settings.getInstance()
		self.htmlRetriever = HtmlRetriever(self.settings.use_proxy)
		#self.htmlRetriever.validate_html_callback = self.validate_html_callback 
		self.parsegoogle = GoogleResultParser()
		
	def pinAjaxQuery(self, title1, title2):
		query = "".join(('"', title1, '" AND "', title2 , '"'))
		query = query.replace(" ", "%20").replace("\"", "%22")
		url = self.settings.ajaxtemplate % query
		return url

	def isInSamePageAjax(self, title1, title2, withProxy=False):
		url = self.pinAjaxQuery(title1, title2)
		print '[GET]:%s' % url
		
		json_result = None
		while json_result is None:
			json_result = self.htmlRetriever.getHTMLByGoogleAjax(url, 3, withProxy)

		max_pages = 4 # 4 * 4 = 16
		pages = 0
		if 'pages' in json_result['responseData']['cursor']:
			pages = len(json_result['responseData']['cursor']['pages'])
		if max_pages > pages:
			max_pages = pages
				
		current_page = 0
		while(current_page < max_pages):
			json = None
			if current_page == 0:
				json = json_result
			else:
				start = current_page * 4
				page_url = "".join((url, "&start=%s" % start))
				print '[GET]:%s' % page_url
				
				while json is None:	
					json = self.htmlRetriever.getHTMLByGoogleAjax(page_url, 3, withProxy)
			
			# process json
			google_results = json['responseData']['results']
			if len(google_results):
				for gr in google_results:
					print "--- ", gr
					if gr['visibleUrl'] in EXCLUDE_NOISE_SITE:
						print '+ found domain:', gr['visibleUrl']
						return True
#					else:	
#						print '- found domain:', gr['visibleUrl']
#						return False
	
			current_page += 1
		return False


	def foundInSamePage(self, url):
		idx = url.find("/");
		domain = ''
		if idx > 0:
			domain = url[0:idx]
		if domain in EXCLUDE_NOISE_SITE:
			return True, domain
		else:
			return False, domain


if __name__ == '__main__':
#	titles = []
	title1 = 'Asymptotic inference for spatial CDFs over time'
	title2 = 'Comparison of spatial variables over subregions using a block bootstrap. Journal of Agricultural, Biological, and Environmental Statistics'
#	titles.append([title1, title2])
#	titles.append([title1, title2])
	checker = checker();
	print checker.isInSamePageAjax(title1, title2)
#	print checker.isInSamePageAjax("Data mining", "Machine Learning")
	url='''http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q="Asymptotic inference for spatial CDFs over time" "Comparison of spatial variables over subregions using a block bootstrap. Journal of Agricultural, Biological, and Environmental Statistics"'''
	url='''http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q="Data mining" "Machine learning"'''


