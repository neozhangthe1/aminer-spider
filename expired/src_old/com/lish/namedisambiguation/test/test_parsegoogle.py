# -*- coding: utf-8 -*-
from com.lish.ajia.util.web import HtmlRetriever
from com.lish.namedisambiguation.parsegoogle import GoogleResultParser
from com.lish.namedisambiguation.settings import Settings
from com.lish.namedisambiguation.checker import checker

class TestCase():

	def __init__(self):
		self.settings = Settings.getInstance()
		self.parsegoogle = GoogleResultParser()
		self.htmlRetriever = HtmlRetriever(self.settings.use_proxy)
		self.checker = checker()

	def test_parse_google_result(self, title1, title2):
		'''Test method extract_from_source.'''
		print '-TEST-:', self.test_parse_google_result.__doc__.strip()
		url = self.checker.pinQuery(title1, title2);
		print '> url', '-' * 100
		print url

		html = self.htmlRetriever.getHtmlRetry(url, 3, False);
		print '> html', '-' * 100
		print html[0:100]
		print '\n'

		print '> blocks', '-' * 100
		models = self.parsegoogle.extract_from_source(html)
		for model in models:
			print model

		print '-END TEST-'


if __name__ == '__main__':
	title1 = 'Asymptotic inference for spatial CDFs over time'
	title2 = 'Comparison of spatial variables over subregions using a block bootstrap. Journal of Agricultural, Biological, and Environmental Statistics'
	test = TestCase();
	# 1. test pinQuery
	url = test.test_parse_google_result(title1, title2)



