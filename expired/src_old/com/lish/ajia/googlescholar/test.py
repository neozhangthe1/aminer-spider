# -*- coding: utf-8 -*-
from com.lish.ajia.util.db import ConstantsDAO, DB
from com.lish.ajia.util.web import HtmlRetriever
import re
from com.lish.pyutil.DataUtil import URLCleaner

class TestCase():

	def __init__(self):
		pass

	def test_retrieve_html(self):
		print 'Test1: test_retrieve_html()'
		url = '''allintitle:"Augmenting Branching Temporal Logics with Existential Quantification over Atomic Propositions" OR "Branching-Depth Hierarchies" OR "On the Relative Succinctness of Nondeterministic Buchi and co-Buchi Word Automata"'''
		url2 = "http://scholar.google.com/scholar?hl=en&num=100&q=%s" % url
		url2 = URLCleaner.encodeUrlForDownload(url2)
		
		url2 = '''http://scholar.google.com/scholar?hl=en&num=100&as_subj=eng&q=%22Finding%20the%20Number%20of%20Factors%20of%20a%20Polynomial%22OR%22Probabilistic%20Models%20of%20Database%20Locking:%20Solutions,%20Computational%20Algorithms,%20and%20Asymptotics%22OR%22The%20AWK%20Programming%20Language%22OR%22Factoring%20Polynomials%20Over%20Algebraic%20Number%20Fields%22'''
		getter = HtmlRetriever(use_proxy=False)
		print getter.getHtmlRetry(url2, 1)

	def test_retrieve_html2(self):
		url = '''allintitle:"Augmenting Branching Temporal Logics with Existential Quantification over Atomic Propositions" OR "Branching-Depth Hierarchies" OR "On the Relative Succinctness of Nondeterministic Buchi and co-Buchi Word Automata"'''
		url2 = "http://scholar.google.com/scholar?hl=en&num=100&q=%s" % url
		url2 = URLCleaner.encodeUrlForDownload(url2)
		getter = HtmlRetriever(use_proxy=True)
		print getter.getHtmlRetry(url2, 1)

	def test_db_constant_dao(self):
		c = ConstantsDAO()
		print 'constant arnet.update.generation is:', c.getConstant("arnet.update.generation")

	def test_db_get_one(self):
		print DB.shortcuts().getOne("select max(wikicfpid) from conference_events")

if __name__ == '__main__':
#	test = TestCase()
#	test.test_retrieve_html()
#	test.test_retrieve_html2()
	#test.test_db_constant_dao()
	#test.test_db_get_one()

	html = '''
	<h3 class=r><a href="http://www.stat.wisc.edu/Department/techreports/tr1069.pdf" target=_blank class=l onmousedown="return clk(0,\'\',\'\',\'res\',\'1\',\'\',\'0CAoQFjAA\')">TECHNICAL REPORT NO. 1069 <em>Asymptotic Inference for Spatial CDFs</em> <b>...</b></a></h3><div class="s"><span class=f>by J Zhu</span> - <span class=f>2002</span> - <a class=fl href="http://scholar.google.com.hk/scholar?hl=en&amp;lr=&amp;cites=5945477102038590596&amp;um=1&amp;ie=UTF-8&amp;ei=CsvBS-q7Nc6TkAW_lrTWBQ&amp;sa=X&amp;oi=science_links&amp;resnum=1&amp;ct=sl-citedby&amp;ved=0CAsQzgIwAA">Cited by 10</a> - <a class=fl href="http://scholar.google.com.hk/scholar?hl=en&amp;lr=&amp;q=related:hKQ6f-yTglIJ:scholar.google.com/&amp;um=1&amp;ie=UTF-8&amp;ei=CsvBS-q7Nc6TkAW_lrTWBQ&amp;sa=X&amp;oi=science_links&amp;resnum=1&amp;ct=sl-related&amp;ved=0CAwQzwIwAA">Related articles</a><br><em>Asymptotic Inference for Spatial CDFs over Time</em>. Jun Zhu, S.N. Lahiri, and Noel Cressie jzhu@stat.wisc.edu http://www.stat.wisc.edu/~jzhu <b>...</b><br><cite>www.stat.wisc.edu/Department/techreports/tr1069.pdf</cite><span class=gl></span>
	'''
	
	
	print '---'
	re_extract_blocks = re.compile("<cite>([^\\x00]+?)</cite>", re.I)
	blocks_html = re.findall(re_extract_blocks, html)
	i = 0
	for block in blocks_html:
		print i, '>>', block
		i += 1
	print '---'

