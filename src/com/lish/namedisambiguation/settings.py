# -*- coding: utf-8 -*-
import os
import re

class Settings():
	'''Settings in Name Disambiguation Application
	'''
	instance = None

	@staticmethod
	def getInstance():
		if Settings.instance is None:
			Settings.instance = Settings()
		return Settings.instance

	def __init__(self):
		self.appname = 'name_disambiguation_google_checker'
		self.debug = True
		self.save_source = True
		self.use_proxy = True

		# fs
		self.basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
		self.resourcedir = os.path.join(self.basedir, 'resources')

		self.source_dir = '/tmp/%s/source' % self.appname
		if not os.path.exists(self.source_dir):
			os.makedirs(self.source_dir)

#		self.pdflink_dir = '/tmp/%s/pdflink' % self.appname
#		if not os.path.exists(self.pdflink_dir):
#			os.makedirs(self.pdflink_dir)

		# templates
		self.urltemplate = "http://www.google.com.hk/search?hl=en&safe=strict&q=%s&meta=&aq=f&aqi=g1&aql=&oq=&gs_rfai="
		self.ajaxtemplate = ''.join(('http://ajax.googleapis.com/ajax/services/search/web',
				'?v=1.0&q=%s'))

		# regexs
		self.re_title_link = re.compile("<h3 class=r><a href=\"([^\"]+?)\"[^>]+?>")
		self.re_extract_blocks = re.compile("li class=g(style=\"mar<gin-left:3em\")?>([^\\x00]+?)</div>", re.I)
		self.re_cite = re.compile("<cite>([^\\x00]+?)</cite>", re.I)


#		self.re_gs_title = re.compile("<h3>(<span class=gs_ct[c|u]>(.+?)</span>\\s+?)?(<a href=\\\"([^\\x00]+?)\\\"[^>]+?>)?([^\\x00]+?)(</a>)?</h3>", re.I)
#
#		self.re_title = re.compile("(.+?)</h3>", re.I)
#		self.re_citedby = re.compile("<span class=gs_fl>(<a[^>]+?>)?Cited by (\\d+)(</a>)?", re.I)
#		self.re_author = re.compile("<span class=gs_a>([^\\x00]+?) - ", re.I)
#		self.re_pdflink = re.compile("<span class=\"gs_ggs gs_fl\"><b><a href=\\\"([^\\\"]+)\\\" [^>]+?>[^<]+</a>", re.I)


if __name__ == '__main__':
	print Settings.getInstance().source_dir





