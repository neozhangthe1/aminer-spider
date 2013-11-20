# -*- coding: utf-8 -*-
from com.lish.ajia.googlescholar.extractor import Extractor
from com.lish.ajia.googlescholar.models import Publication
from com.lish.ajia.googlescholar.pubmatcher import PubMatcher
from com.lish.pyutil.DataUtil import URLCleaner
from com.lish.ajia.googlescholar.settings import Settings

class TestCase():

	def __init__(self):
		self.extractor = Extractor().getInstance()
		self.settings = Settings.getInstance()

	def integrate_test_pubs(self, pub_candidates):
		'''
			For Debug Errors
		'''
		print '- INTEGRATE TEST -:', self.integrate_test_pubs.__doc__.strip()

		extractor = Extractor.getInstance()
		matcher = PubMatcher.getInstance()
		
		# print queries
		query, used_pubs = Extractor.pinMaxQuery(pub_candidates)
		print 'Test %s pub, query: \n\t%s' % (len(used_pubs), query)
		url = self.settings.urltemplate_by_pubs % URLCleaner.encodeUrlForDownload(query)
		# url = URLCleaner.encodeUrlForDownload(url)
		print "\t", url
		
		# do
		all_models = extractor.getNodesByPubs(used_pubs)
		(pubs_found, pubs_notfound) = matcher.matchPub(used_pubs, all_models, debug_output=True)
		
		# print out
		print '-' * 100
		for pub in pubs_found:
			print '[%s] %s' % (pub.ncitation, pub)
		print '-' * 100
		for pub in pubs_notfound:
			print '[%s] %s' % ('-', pub)
		print '-' * 100
		print '- test done -'

	def integrate_test_persons(self, pub_candidates):
		pass
	
	def testpubs(self):
		debug_history = []
		# Bad Reals.
		debug_history.append(Publication(-1, 2000,
			'OQL[C++]: Extending C++ with an Object Query Capability.', "pubkey", -1,
			"Jose A. Blakeley", -5))
		
		not_fixed = []
		not_fixed.append(Publication(-1, 2000,
			'On View Support in Object-Oriented Databases Systems.', "pubkey", -1,
			"Won Kim,William Kelley", -5))
		not_fixed.append(Publication(-1, 2000,
			'The POSC Solution to Managing EP Data.', "pubkey", -1,
			"Vincent J. Kowalski", -5))
		not_fixed.append(Publication(-1, 2000,
			'Query Processing in Object-Oriented Database Systems.', "pubkey", -1,
			"M. Tamer Ozsu,Jose A. Blakeley", -5))
		
#		now_test.append(Publication(-1, 2000,
#			'On sensing capacity of sensor networks for the class of linear observation, fixed SNR models.', "pubkey", -100,
#			"Shuchin Aeron, Manqi Zhao, Venkatesh Saligrama.", -5))
#		now_test.append(Publication(-1, 2000,
#			'Wireless ad-hoc networks: Strategies and Scaling laws for the fixed SNR regime', "pubkey", -100,
#			"Shuchin Aeron, Manqi Zhao, Venkatesh Saligrama.", -5))
		
		now_test = []
		
		now_test.append(Publication(-1, 2000,
			'The Kuramoto model: A simple paradigm for synchronization phenomena', "pubkey", -100,
			"Alexandre Eudes, Maxime Lhuillier.", -5))
		
		self.integrate_test_pubs(now_test);
		
	def testPerson(self):
		pass


	def debugTest(self):
		pass

######################################################################
if __name__ == '__main__':
	test = TestCase()
#	test.testpubs()
	#test.testPerson()
	test.debugTest();

# Known problems:
# On view support in object-oriented database systems











