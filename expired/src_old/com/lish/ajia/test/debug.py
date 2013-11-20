# -*- coding: utf-8 -*-
from com.lish.ajia.googlescholar.daos import PublicationDao
from com.lish.ajia.googlescholar.extractor import Extractor
from com.lish.ajia.googlescholar.models import Publication
from com.lish.ajia.googlescholar.pdfsaver import PDFLinkSaver
from com.lish.ajia.googlescholar.pubmatcher import PubMatcher
from com.lish.ajia.googlescholar.settings import Settings

class DebugSuit():

	def __init__(self):
		self.extractor = Extractor.getInstance()
		self.matcher = PubMatcher.getInstance()
		self.pubdao = PublicationDao()

	def debug_person(self, person_id, person_name, generation):
		'''Test method extract_from_source.'''
		print '- DEBUG Person "%s" -:' % person_name

		pubs = self.pubdao.getPublicationByPerson(person_id, generation)
		all_models = self.extractor.getNodesByPersonName(person_name)
#		if True:#print all all_models
#			print '-' * 100, 'This is all_models'
#			for key, models in all_models.items():
#				print key, ':'
#				for model in models:
#					print '\t', model.readable_title, '(', model, ')'
#			print '=' * 100 , 'all_models print done'
		(pubs_found, pubs_notfound) = PubMatcher.getInstance().matchPub(pubs, all_models)
		for pub in pubs_found:
			print 'pubs found' , pub
		print '-' * 100
		for pub in pubs_notfound:
			print 'not found' , pub

		print '|||||||||||||||||||||||||||| get by pubs '
		# todo here should be a while
		query, used_pubs = Extractor.pinMaxQuery(pubs_notfound)
		print '%s pub, query: %s' % (len(used_pubs), query)
		all_models = self.extractor.getNodesByPubs(used_pubs)
		(pubs_found, pubs_notfound) = PubMatcher.getInstance().matchPub(used_pubs, all_models)
		for pub in pubs_found:
			print 'pubs found' , pub
		print '-' * 100
		for pub in pubs_notfound:
			print 'not found' , pub

		print '- END DEBUG -'

	def debug_pubs(self):
		'''Debug get by pub'''
		print '-TEST-:', self.debug_pubs.__doc__.strip()
		#----------------------------------------------------
		pub_candidates = []
		
		# group 1
#		pub_candidates.append(Publication(-1, 2000, 'Some Reflections on Proof Transformations', "pubkey", -1, "Peter B. Andrews", -5))
#		pub_candidates.append(Publication(-1, 2000, 'Theorem Proving via General Mappings', "pubkey", -1, "Peter B. Andrews", -5))
#		pub_candidates.append(Publication(-1, 2000, 'Connections and Higher-Order Logic', "pubkey", -1, "Peter B. Andrews", -5))
#		pub_candidates.append(Publication(-1, 2000, 'The TPS Theorem Proving System', "pubkey", -1, "Peter B. Andrews,Sunil Issar,Dan Nesmith,Frank Pfenning", -5))
		
		# group 2
#		pub_candidates.append(Publication(-1, 2000, 'Linearizable concurrent objects', "pubkey", -1, "MP Herlihy, JM Wing", -5))
#		pub_candidates.append(Publication(-1, 2000, 'Protein structure prediction using a combination of sequence homology and global energy minimization I. Global energy minimization of surface loops', "pubkey", -1, "MJ Dudek, HA Scheraga", -5))
		
		# group 3
#		pub_candidates.append(Publication(-1, 2000, 'Implementation of Prolog databases and database operation builtins in the WAM-Plus model', "pubkey", -1, "Z Chenxi, C Yungui, L Bo", -5))

		# group 4
		pub_candidates.append(Publication(-1, 2000, 'Procedural Semantics for Fuzzy Disjunctive Programs on Residuated Lattices', "pubkey", -1, "Dusan Guller", -5))
		
		extractor = Extractor.getInstance()
		query, used_pubs = Extractor.pinMaxQuery(pub_candidates)
		print '%s pub, query: %s' % (len(used_pubs), query)

		#
		# Get WEB PAGE
		#
		use_web = True # ***************
		if use_web:
			all_models = extractor.getNodesByPubs(used_pubs)
		else:
			f = file('debug_pubs.txt', 'r')
			html = f.read()
			models = self.extractor.extract_from_source(html)
			all_models = self.extractor._Extractor__merge_into_extractedmap(None, models)

		print '\n- all_models ----------------------'
		if all_models is not None:
			for key, models in all_models.items():
				print key
				for model in models:
					print "\t", model
		else:
			print 'all_models is None'
		print '- all_models end ----------------------\n'

		(pubs_found, pubs_notfound) = PubMatcher.getInstance().matchPub(used_pubs, all_models)
		for pub in pubs_found:
			print 'pubs found' , pub
		print '-' * 100
		for pub in pubs_notfound:
			print 'not found' , pub
		print '- test done -'

if __name__ == '__main__':
	''' top pub person， this is in local database.
	'''
	debug = DebugSuit()
#	debug.debug_person(29463, 'Reihaneh Safavi-Naini', 4)
	debug.debug_pubs()


	# end
	if Settings.getInstance().save_pdflink:
		PDFLinkSaver.getInstance().flush()



