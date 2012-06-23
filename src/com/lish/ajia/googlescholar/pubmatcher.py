# -*- coding: utf-8 -*-
'''
Runner Platform Module: DB
KEG | elivoa | gmail.com
Time-stamp: "root 2009/07/24 13:04:13"
'''

#from runner.proxy import proxy
from com.lish.ajia.googlescholar import models
from com.lish.ajia.googlescholar.daos import PublicationDao
from com.lish.ajia.googlescholar.extractor import Extractor
from com.lish.pyutil.DataUtil import GoogleDataCleaner
from settings import Settings
from Decorator import ClassBeforeUnicode
import os
import re
import editdist

class PubMatcher:
	'''Match GoogleCitationResults into PublicationModel by title, authors, year and so on.
	'''
	__instance = None

	@staticmethod
	def getInstance():
		if PubMatcher.__instance is None:
			PubMatcher.__instance = PubMatcher()
		return PubMatcher.__instance

	def __init__(self):
		self.settings = Settings.getInstance()
		self.debug = self.settings.debug


	def matchPub(self, pubs, extracted_map, check_person=False, debug_output=False):
		'''Match pub with extracted
		@return (pubs_matched, pubs_not_matched)
		@params:
			pubs - Publication read from database.
			extracted_map - same with all_models {key_title:[ExtractedModel,...]}
			check_person - if True, will check if authors is matched with authors in db.(will ignore ...).
				default False. Search using author:xxx do not need author check, this work is done by google.
		'''
		if pubs is None or len(pubs) == 0: 
			return [], pubs
		if extracted_map is None or len(extracted_map) == 0: 
			return [], pubs
		if self.debug and False: 
			print 'match %s pubs in %s extracted items' % (len(pubs), len(extracted_map))
			
		# match
		print_not_matched = False
		pubs_matched = []
		pubs_not_matched = []

		for pub in pubs:
			cleanned_tuple = GoogleDataCleaner.cleanGoogleTitle(pub.title)
			key_title = cleanned_tuple[1]
			has_dot = cleanned_tuple[2]
			
			# First Match, select loose match. ExtractedPub List
			models = []
			
			# different with v1, a looser match.
			# title allow 10% mistake.
			# author loose match.
			for short_key, extracted_models in extracted_map.items():
				matched = False
				if has_dot:
					# ignore and contains
					if key_title.find(short_key) != -1:
						matched = True
						_m = extracted_models
						for m in _m: # Add Loose Value
							m.looseValue += 1;
						models.extend(_m)
				else:
					# direct match
					if key_title == short_key:
						matched = True
						_m = extracted_map[key_title]
						for m in _m: # Add Loose Value
							m.looseValue += 0;
						models.extend(_m);
			
				# try loose match
				if not matched:
					ed = editdist.distance(short_key, key_title)
					if ed < 10:
						looseValue = float(len(key_title)) * (10 / float(100))
						if looseValue > ed: # remove ed not match much
							_m = extracted_models
							for m in _m:
								m.looseValue += ed;
							models.extend(_m)
#							if True and ed < 10:
#								print '-' * 100
#								print 'title: %s ' % key_title
#								print 'short: %s ' % short_key
#								print 'ed is: %s ' % ed
#								print 'loose: %s ' % looseValue
					
			# Exact match, select who is the right one.
			if models is not None and len(models) > 0:
				max_citation_model = None
				for model in models:
					if model.authors is None or \
					self.matchAuthors(model.authors, pub.authors, debug_output=False, debug_title=model.title):  # if author matched.
						if max_citation_model is None or int(max_citation_model.ncitation) < int(model.ncitation):
							max_citation_model = model
				# select max citation?
				if max_citation_model is not None:
					if  max_citation_model.ncitation >= pub.ncitation: 
						pub.ncitation = max_citation_model.ncitation
						pub.increased = max_citation_model.ncitation - pub.ncitation

					pub.pdflink = max_citation_model.pdfLink
					pub.web_url = max_citation_model.web_url
					pubs_matched.append(pub)
					if pub.pdflink is None:
						file_object = open('web_url.txt', 'a')
						web_url= pub.web_url
						Id = str(pub.id)
						Title = pub.title
						Author = str(pub.authors)
						file_object.write(" ".join([Id, Title, Author, web_url]))
						file_object.write("\n")
						file_object.close()
					else: 
						file_object = open('paper_link.txt', 'a')
						Id = str(pub.id)
						Title = pub.title
								
						Pdflink = str(pub.pdflink)
						Author = str(pub.authors)
						file_object.write(" ".join([Id, Title, Author, Pdflink]))
						file_object.write("\n")
						file_object.close()

		for pub in pubs:
			title = pub.title
			found = False;
			for matched in pubs_matched:
				if title == matched.title:
					found = True
					break
			if not found:
				pubs_not_matched.append(pub)
				if print_not_matched: 
					print 'this pub not matched: ', pub

		return (pubs_matched, pubs_not_matched)

	# Title loose match
	def _titleLooseMatch(self):
		'''Title Match Stratage:
			1. Any title can ignore edit distance 1
			2. Long title can ignore edit distance 10%
		'''
		
	

	# debug print.
	def _printExtractedPubMap(self, extracted_map):
		for key, mpubs in extracted_map.items():
			print '-k-:%s' % key
			for mpub in mpubs:
				print '  ', mpub.asDetailText()
				
	# Changed From Version 2
	def matchAuthors(self, google_author_string, authors, debug_title="", debug_output=False):
		'''If the two author string matched, return True
		@return: boolean - True if matched, otherwise False.
		@param:
		- google_author_string, e.g.
			… DeSmedt, W Du, W Kent, MA Ketabchi, WA … - …, 1991 - doi.ieeecomputersociety.org
			R Ahmed, P DeSmedt, W Du, W Kent, MA … - …, 1991 - doi.ieeecomputersociety.org
			 
		- authors, e.g.
			Rafi Ahmed,Philippe De Smedt,Weimin Du,William Kent,Mohammad A. Ketabchi,Witold Litwin,Abbas Rafii,Ming-Chien Shan
		'''
		matcher = AuthorMatcher(debug=debug_output, debug_title=debug_title);
		matcher.setBaseAuthorString(authors);
		matcher.setGoogleScholarAuthorString(google_author_string);
		matcher.prepare();
		if matcher.simpleMatch():
			return True
		if matcher.looseMatch():
			return True
		return False
		

#
# AuthorMatcher Class
#
class AuthorMatcher:
	'''Use loose condition to match. One is google string, One is standard authors.
	@return: True if 2 author string matched.  
	'''
	def __init__(self, debug=False, debug_title="---"):
		self.authorStringBase = ''		# 'base' is ours.
		self.authorStringToMatch = ''	# 'to match' is from google.
		self.ignore_left = False	# for toMatch
		self.ignore_right = False	# for toMatch

		self.authorFeatureBase = '';
		self.authorFeatureToMatch = '';
		
		self.ignore_sign_1 = '&hellip;'
		self.ignore_sign_2 = u'\\xe2\\x80\\xa6'
		
		self.debug = debug
		self.debug_title = debug_title
	
	def setBaseAuthorString(self, baseAuthorString):
		self.authorStringBase = baseAuthorString
	
	def setGoogleScholarAuthorString(self, googleAuthorString):
		(self.ignore_left, self.ignore_right, self.authorStringToMatch) = \
			self.cleanGoogleScholarAuthorString(googleAuthorString);
	
	def prepare(self):
		self.authorFeatureBase = self.__trans_to_compact_array(self.authorStringBase, False, False);
		self.authorFeatureToMatch = self.__trans_to_compact_array(self.authorStringToMatch, self.ignore_left, self.ignore_right)
		if self.debug:
			print 'base fea:', ','.join(self.authorFeatureToMatch)
			print 'to match:', ','.join(self.authorFeatureBase)
		
	# changed from v2, if 2 authors signature in google exists in our authors, we treat these 2 author String matched.
	def simpleMatch(self):
		total_from_google = 0
		matched = 0
		for authorSigntureGoogle in self.authorFeatureToMatch:
			total_from_google += 1
			if authorSigntureGoogle in self.authorFeatureBase:
				matched += 1
		
		if total_from_google <= 2:
			# common process = v2
			featureStringBase = ",".join(self.authorFeatureBase).lower()
			featureStringToMatch = ",".join(self.authorFeatureToMatch).lower()
			if not self.ignore_left and not self.ignore_right:
				if(featureStringBase == featureStringToMatch):
					return True;
			if self.ignore_left and not self.ignore_right: #...xx,xx
				if(featureStringBase.endswith(featureStringToMatch)):
					return True;
			elif not self.ignore_left and self.ignore_right:  #xx,xx...
				if(featureStringBase.startswith(featureStringToMatch)):
					return True;
			elif self.ignore_left and self.ignore_right:
				if featureStringBase.find(featureStringToMatch) >= 0:
					return True
			else:
				return False
		
		else:
			return matched >= 2;
	
	def looseMatch(self, verbose_output=False):
		'''Strategy:
		'''
		matched = 0
		not_matched = 0;
		total_authors = len(self.authorFeatureBase)
		if not self.ignore_left:
			# first 2 authors must match
			for i in range(0, min(2, len(self.authorFeatureBase), len(self.authorFeatureToMatch))):
				if self.authorFeatureBase[i] == self.authorFeatureToMatch[i]:
					matched += 1
				else:
					# first 2 author not matched
					return False;

		# first item
		start_index = matched
		if self.ignore_left:
			f = self.authorFeatureToMatch[start_index] # must be 0
			found = False
			for fb in self.authorFeatureBase:
				if fb.endswith(f):
					found = True
					break
			if found :
				matched += 1
			else:
				not_matched += 1
			start_index += 1
			
		# last item
		end_index = len(self.authorFeatureToMatch) - 1
		if self.ignore_right:
			f = self.authorFeatureToMatch[end_index] 
			found = False
			for fb in self.authorFeatureBase:
				if fb.startswith(f):
					found = True
					break
			if found :
				matched += 1
			else:
				not_matched += 1
			end_index -= 1
		
		# others
		for f in self.authorFeatureToMatch[start_index:end_index + 1]:
			found = False
			for fb in self.authorFeatureBase:
				if fb == f:
					found = True
					break
			if found :
				matched += 1
			else:
				not_matched += 1

		loose_matched = False		
		if not_matched == 0 and matched == len(self.authorFeatureToMatch):
			loose_matched = True
		if (not_matched + matched) / 4 >= not_matched:
			loose_matched = True
		
		if loose_matched and verbose_output:
			verbose = []
			verbose.append(' ------------Author Match True -------------------------------------')
			verbose.append(' --TITLE: %s' % self.debug_title)
			verbose.append(' --AuthorMatcher--:base author:%s' % self.authorStringBase)
			verbose.append(' --AuthorMatcher--:to Match au:%s' % self.authorStringToMatch)
			verbose.append(' --AuthorMatcher--:baseFeature:%s' % ','.join(self.authorFeatureBase))
			verbose.append(' --AuthorMatcher--:to Match fe:%s' % ','.join(self.authorFeatureToMatch))
			verbose.append(' --AuthorMatcher--:matched %s, notMatched %s, total:%s, total base:%s' % \
				(matched, not_matched, len(self.authorFeatureToMatch), total_authors))
			verbose.append(' -------------------------------------------------------------------')
			print '\n'.join(verbose)
		
		return loose_matched

	#@staticmethod
	@ClassBeforeUnicode
	def cleanGoogleScholarAuthorString(self, google_author_string):
		'''@return: (boolean ignoreLeft, boolean ignoreRight, String trimedString) 
		'''
		if self.debug: print '--debug--:[Clean0]: ', google_author_string
		
		# step 1: remove everything after ' - '
		indexOfPlusSign = google_author_string.find(' - ')
		if indexOfPlusSign != -1:
			google_author_string = google_author_string[:indexOfPlusSign]
		google_author_string = google_author_string.strip();
		if self.debug: print '--debug--:[Clean1]: ', google_author_string
		
		ignore_left = google_author_string.startswith(self.ignore_sign_1) \
			or google_author_string.startswith(self.ignore_sign_2)
		ignore_right = google_author_string.endswith(self.ignore_sign_1) \
			or google_author_string.endswith(self.ignore_sign_2)
		
		google_author_string = re.sub("(<(.*?)>)", "", google_author_string)
		google_author_string = re.sub("[^A-Za-z0-9,\s]", "", google_author_string)
		google_author_string = re.sub("\\s+", " ", google_author_string)
		google_author_string = google_author_string.strip()
		
		if self.debug: print '--debug--:[Clean3]: ', ignore_left, ignore_right, google_author_string
		return (ignore_left, ignore_right, google_author_string)
	
	def __trans_to_compact_array(self, str_authors, ignore_left, ignore_right):
		authors = str_authors.split(',')
		compact = []
		for i in range(0, len(authors)):
			author = authors[i].strip()
			if i == 0 and ignore_left:
				compact.append(author[-1:])
			elif i == len(authors) - 1 and ignore_right:
				compact.append(author[0:1])
			else:
				compact.append("".join((author[:1], author[-1:])))
		return compact
			
			
class TestPubMatcher:
	def __init__(self):
		self.matcher = PubMatcher()
		
	#
	# Test
	#
	def test_matchPub(self):
		self.extractor = Extractor().getInstance()
		pubdao = PublicationDao()
		person_id = 13419
		person_name = 'jie tang'
		# Read sources from files
		all_models = {}
		for page in range(0, 3):
			filename = "".join((person_name, '_page_', str(page), '.html'))
			f = file(os.path.join(self.settings.source_dir, filename), 'r')
			html = f.read()
			models = self.extractor.extract_from_source(html)
			if models is not None:
				self.extractor._Extractor__merge_into_extractedmap(all_models, models)
		print 'Total found DEBUG  %s items.' % len(all_models)

		# part 2
		pubs = pubdao.getPublicationByPerson(person_id, self.settings.generation)

		printout = False
		if printout:
			for key, models in all_models.items():
				print key, " --> ", models
			print '==================='
			for pub in pubs:
				print pub

		(pubs_matched, pubs_not_matched) = self.matchPub(pubs, all_models)
		print '- test done -', len(pubs_matched), len(pubs_not_matched)
		return pubs_not_matched

	def test_fetchByPubs(self, pubs):
		'''Test use a list of pubs that not found in person search'''
		print '-- test fetchByPubs %s pubs', len(pubs)
		new_pubs = []
		for pub in pubs:
			new_pubs.append((pub, 'jie tang'))

		extractor = Extractor()
		extractor.getNodesByPubs(new_pubs)
		print '- test done -'

	def test_match_with_authors(self):
		data_test = (
			('… DeSmedt, W Du, W <b>Kent</b>, MA Ketabchi, WA … - …, 1991 - doi.ieeecomputersociety.org',
			 'Rafi Ahmed,Philippe De Smedt,Weimin Du,William Kent,Mohammad A. Ketabchi,Witold Litwin,Abbas Rafii,Ming-Chien Shan'),
			('R Ahmed, P DeSmedt, W Du, W Kent, MA … - …, 1991 - doi.ieeecomputersociety.org',
			 'Rafi Ahmed,Philippe De Smedt,Weimin Du,William Kent,Mohammad A. Ketabchi,Witold Litwin,Abbas Rafii,Ming-Chien Shan'),
			('P Lyngbaek, W Kent - … on the 1986 international workshop on Object …, 1986 - portal.acm.org',
			 'Peter Lyngbak,William Kent'),
			('W Kent - Proceedings of the 8th Bristish National …, 1990 - fog.hpl.external.hp.com',
			 'William Kent'),
			('DE Neiman, DW Hildum, VR Lessef, T  &hellip;',
			 'Daniel E. Neiman,David W. Hildum,Victor R. Lesser,Tuomas Sandholm'),
			('M Esmaili, R Safavi-Naini, J Pieprzyk',
			 'Mansour Esmaili,Reihaneh Safavi-Naini,Josef Pieprzyk'),
			 ('DH Fishman, J Annevelink, E Chow, T  &hellip;',
			 'Daniel H. Fishman,Jurgen Annevelink,David Beech,E. C. Chow,Tim Connors,J. W. Davis,Waqar Hasan,C. G. Hoch,William Kent,S. Leichner,Peter Lyngbak,Brom Mahbod,Marie-Anne Neimat,Tore Risch,Ming-Chien Shan,W. Kevin Wilkinson')
		)
		data_debug = (
			('DH Fishman, J Annevelink, E Chow, T  &hellip;',
			 'Daniel H. Fishman,Jurgen Annevelink,David Beech,E. C. Chow,Tim Connors,J. W. Davis,Waqar Hasan,C. G. Hoch,William Kent,S. Leichner,Peter Lyngbak,Brom Mahbod,Marie-Anne Neimat,Tore Risch,Ming-Chien Shan,W. Kevin Wilkinson'),
		)
		for ga, da in data_debug:
			print "match: %s \n with: %s \n   is: %s" % (ga, da, \
					 self.matcher.matchAuthors(ga, da, debug_output=True))

			
			
if __name__ == '__main__':
	test = TestPubMatcher()
	# test suit 1
#	pubs_not_matched = test.test_matchPub()
#	test.test_fetchByPubs(pubs_not_matched)
	test.test_match_with_authors()


