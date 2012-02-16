# -*- coding: utf-8 -*-
import os
import re

class Settings():

	instance = None

	@staticmethod
	def getInstance():
		if Settings.instance is None:
			Settings.instance = Settings()
		return Settings.instance

	def __init__(self):
		self.debug = True
		self.save_source = False
		self.save_pdflink = True
		self.use_proxy = True
		self.generation = 0; # mutable
		# Debug One Person Run
		self.byid = False
		
		self.max_person_thread = 10 
		self.max_pub_thread = 10
		
		# db
#		self.db_host = "10.1.1.110"
#		self.db_user = "root"
#		self.db_passwd = "keg2012"
#		self.db_database = "arnet_db"
		
		self.db_host = "arnetminer.org"
		self.db_user = "root"
		self.db_passwd = "eserver409$)("
		self.db_database = "arnet_db"
		
#		self.db_host = "localhost"
#		self.db_user = "root"
#		self.db_passwd = "root"
#		self.db_database = "arnet_local"

		# fs
		self.basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
		self.resourcedir = os.path.join(self.basedir, 'resources')
		self.outputdir = os.path.join(self.basedir, 'output')
		
		self.source_dir = os.path.join(self.outputdir, 'google_citation', 'source')
		if not os.path.exists(self.source_dir):
			os.makedirs(self.source_dir)
			
		self.pdflink_dir = os.path.join(self.outputdir, 'google_citation', 'pdflink')
		if not os.path.exists(self.pdflink_dir):
			os.makedirs(self.pdflink_dir)

		# templates
		self.urltemplate_by_person_page = "http://scholar.google.com/scholar?start=%s&q=%s&hl=en&num=100&as_subj=eng"
		self.urltemplate_by_pubs = 		  "http://scholar.google.com/scholar?hl=en&num=100&q=%s"

		# regexs
		
		# @update by gb 2010-05-06, because google changed it's page
		# self.re_extract_blocks = re.compile("<div class=gs_r>([^\\x00]+?)</div>", re.I)
		self.str_blocks_spliter = '<div class=gs_r>'  
#		self.re_gs_title = re.compile("<h3>(<span class=gs_ct[c|u]>(.+?)</span>\\s+?)?(<a href=\\\"([^\\x00]+?)\\\"[^>]+?>)?([^\\x00]+?)(</a>)?</h3>", re.I)
		self.re_gs_title = re.compile('<h3 class="gs_rt">', re.I)
		self.re_title = re.compile("(.+?)</h3>", re.I)
		self.re_citedby = re.compile("<span class=gs_fl>(<a[^>]+?>)?Cited by (\\d+)(</a>)?", re.I)
		self.re_author = re.compile("<span class=gs_a>([^\\x00]+?) - ", re.I)
		# self.re_pdflink = re.compile("<span class=\"gs_ggs gs_fl\"><b><a href=\\\"([^\\\"]+)\\\" [^>]+?>[^<]+</a>", re.I)
		self.re_pdflink = re.compile("<span class=\"gs_ggs gs_fl\"><a href=\"([^\\\\\"]+)\" [^>]+?><span class=gs_ctg2>\\[PDF]+?</span>", re.I)
		
		# Program running configs
		# store cache size config
		self.person_cache_size	 	 = 1500
		self.pub_cache_size 		 = 20000


if __name__ == '__main__':
	print os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../resources"))





