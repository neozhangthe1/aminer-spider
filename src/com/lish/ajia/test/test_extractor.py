# -*- coding: utf-8 -*-
from com.lish.ajia.googlescholar.extractor import Extractor
from com.lish.ajia.googlescholar.models import Publication
from com.lish.ajia.googlescholar.pubmatcher import PubMatcher

class TestCase():

	def __init__(self):
		self.extractor = Extractor().getInstance()


	def test_extractFromPage(self):
		'''Test method extract_from_source.'''
		print '-TEST-:', self.test_extractFromPage.__doc__.strip()
		# prepare
		f = file("../test/example_google_page.txt", "r")
		html = f.read()
		f.close()
		
		# test
		models = self.extractor.extract_from_source(html)
		print "**:>> %s" % len(models)
		for model in models:
			print model.asDetailText();
			
		print '-END TEST-'


if __name__ == '__main__':
	test = TestCase()
	test.test_extractFromPage()



