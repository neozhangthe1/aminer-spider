# -*- coding: utf-8 -*-
from com.lish.ajia.googlescholar.settings import Settings
import Queue
import datetime
import os


class PDFLinkSaver:
	__instance = None

	@staticmethod
	def getInstance():
		if PDFLinkSaver.__instance is None:
			PDFLinkSaver.__instance = PDFLinkSaver()
		return PDFLinkSaver.__instance

	def __init__(self):
		self.settings = Settings.getInstance()
		self.debug = self.settings.debug
		self.linkcache = Queue.Queue()
		self.running = True  #sync ed with main running flag in mgr_interval_thread
		
		now = datetime.datetime.now()
		filepath = "pdflink_%s_%s_%s_%s_%s.list" % (now.year, now.month, now.day, now.minute, now.second)
		self.pdflink_file = file(os.path.join(self.settings.pdflink_dir, filepath), 'w')

	def add(self, title, link):
		try:
			if title is not None and link is not None:
				self.linkcache.put((title, link))
		except Exception, e:
			print e

	def flush(self):
		''' 将内存中缓存的已经抓取的pub批量存入数据库中。'''
		try:
			while self.linkcache.not_empty:
				title, link = self.linkcache.get(False)
				self.pdflink_file.write("%s\t%s\n" % (title, link))
		except Exception, e:
			print e
		self.pdflink_file.flush()
		
	def close(self):
		if self.pdflink_file:
			self.pdflink_file.flush()
			self.pdflink_file.close()
