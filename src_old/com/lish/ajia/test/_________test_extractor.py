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
		for model in models:
			print model
		print '-END TEST-'


	def test_getNodesByPersonName(self):
		'''Test method getNodesByPersonName.'''
		print '-TEST-:', self.test_extractFromPage.__doc__.strip()
		e = Extractor()
		models = e.getNodesByPersonName('jie tang')
		for model in models:
			print model
		print '-END TEST-'


	def test_clean_title(self):
		html = '''<p><div class=gs_r><h3><a href="http://doi.ieeecomputersociety.org/10.110910.1109/ICDM.2001.989541" onmousedown="return clk(this.href,'','res','16')">CMAR: Accurate and efficient classification based on multiple class-association  &hellip;</a></h3><span class="gs_ggs gs_fl"><b><a href="http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.24.9014&amp;rep=rep1&amp;type=pdf" onmousedown="return clk(this.href,'gga','gga','16')">psu.edu</a> <span class=gs_ctg>[PDF]</span></b></span><font size=-1><br><span class=gs_a>WLJ Han, J Pei - Proc. of IEEE-ICDM, 2001 - doi.ieeecomputersociety.org</span><br>Previous studies propose that associative classification has high classification accuracy and <br>
strong flexibility at handling unstructured data. However, it still suffers from the huge set of mined <br>
rules and sometimes biased classi- fication or overfitting since the classification is based <b> ...</b> <br><span class=gs_fl><a href="/scholar?cites=1090097156101892771&amp;hl=en&amp;num=100&amp;as_sdt=2000">Cited by 511</a> - <a href="/scholar?q=related:o-odgJbNIA8J:scholar.google.com/&amp;hl=en&amp;num=100&amp;as_sdt=2000">Related articles</a> - <a href="/scholar?cluster=1090097156101892771&amp;hl=en&amp;num=100&amp;as_sdt=2000">All 28 versions</a></span></font>  </div>  <p><div class=gs_r><h3><a href="http://portal.acm.org/citation.cfm?id=347167" onmousedown="return'''
		models = self.extractor.extract_from_source(html)
		for model in models: print model
		print '- test done -'


	def test_debug_not_found(self):
		'''Debug Errors'''
		print '-TEST-:', self.test_extractFromPage.__doc__.strip()

		pub_candidates = []
		pub_candidates.append(Publication(-1, 2000, 'Formalizzazione e Ottimizzazione di Transazioni di modifica in CLP(AD)', "pubkey", -1, "authors", -5))
		#----------------------------------------------------
		pub_candidates = []
		pub_candidates.append(Publication(-1, 2000, 'On the Use of Spreading Activation Methods in Automatic Information Retrieval', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Chairman\'s Message', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Introduction to Modern Information Retrieval', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Publications', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Die RISC-CISC Debatte', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Kryptologie', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Approximative Public-Key-Kryptosysteme', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Integritat in IT-Systemen', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Vollstandige Reduktionssysteme', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Approximative Public-Key-Kryptosysteme', "pubkey", -1, "authors", -5))

		matcher = PubMatcher.getInstance()
		extractor = Extractor.getInstance()
		query, used_pubs = Extractor.pinMaxQuery(pub_candidates)
		print '%s pub, query: %s' % (len(used_pubs), query)
		all_models = extractor.getNodesByPubs(used_pubs)
		(pubs_found, pubs_notfound) = PubMatcher.getInstance().matchPub(used_pubs, all_models)
		for pub in pubs_found:
			print 'pubs found' , pub
		print '-' * 100
		for pub in pubs_notfound:
			print 'not found' , pub
		print '- test done -'


	def test_pin_query(self):
		'''Test pin query'''
		print '-TEST-:', self.test_extractFromPage.__doc__.strip()
		#----------------------------------------------------
		pub_candidates = []
		pub_candidates.append(Publication(-1, 2000, 'Language, Cohesion and Form Margaret Masterman (1910-1986) (Edited by Yorick Wilks, University of Sheffield), Cambridge University Press (Studies in natural language processing, edited by Steven Bird and Branimir Boguraev), 2005, x+312 pp; hardbound, ISBN 0-521-45489-1', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Methodology and technology for virtual component driven hardware/software co-design on the system-level', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'From the Editor: Security Cosmology: Moving from Big Bang to Worlds in Collusion', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'XML for the Exchange of Automation Project Information', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Editor\'s Notes', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Integrating Mathematical and Symbolic Models Through AESOP: An Expert for Stock Options Pricing', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Von Transaktionen zu Problemlosungszyklen: Erweiterte Verarbeitungsmodelle fur Non-Standard-Datenbanksysteme', "pubkey", -1, "authors", -5))
		pub_candidates.append(Publication(-1, 2000, 'Schemazusammenfuhrungen mit Vorgaben: Eine Studie uber die STEP-Norm AP214 und Oracle\'s Flexfelder', "pubkey", -1, "authors", -5))
		query, pubs = self.extractor.pinMaxQuery(pub_candidates)
		print query
		for pub in pubs:
			print pub


if __name__ == '__main__':
	test = TestCase()
#	test.test_extractFromPage()
#	test.test_getNodesByPersonName()  # get all page by jie and save to temp
#	test.test_clean_title()
#	test.test_debug_not_found()
	test.test_pin_query()



