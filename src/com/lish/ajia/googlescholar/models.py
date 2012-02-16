# -*- coding: utf-8 -*-

# Publication
class ExtractedGoogleScholarResult:
	# id, year, title, pubkey, jconf, authors
	def __init__(self):
		self.id = id			# placeholder to match with publication.
		self.gs_type = None
		self.title = None
		self.readable_title = None		# cleaned title.
		self.shunked_title = None		# used as key.
		self.title_has_dot = None		# boolean, if title has ...
		self.ncitation = -1
		self.authors = None                # ?
		self.pdfLink = None				# PDF Link
		self.looseValue = 0				# loose value, lower matcher, 0 all match
		self.web_url = None	

	def __str__(self):
		return "title(%s,authors:%s) cited by %s." % (self.readable_title, self.authors, self.ncitation)

	def asDetailText(self):
		stack = []
		stack.append("GoogleScholarResult: %s\n" % self.id);
		stack.append("  KEY  :%s\n" % self.shunked_title);
		stack.append("  CLEAN:%s\n" % self.readable_title);
		stack.append("  TITLE:%s\n" % self.title);
		stack.append("  Authors :%s\n" % self.authors);
		stack.append("  Citation:%s\n" % self.ncitation);
		stack.append("  PDF Link:%s\n" % self.pdfLink);
		return ''.join(stack);

# Publication
class Publication:
	''' Publication Model for update citation'''

	# id, year, title, pubkey, jconf, authors
	def __init__(self, id, year, title, pubkey, jconf, authors, ncitation):
		self.id = id
		self.year = year
		self.title = title
		self.pubkey = pubkey
		self.jconf = jconf
		self.authors = authors
		self.ncitation = ncitation
		self.web_url = None
		self.pdflink = None
		self.startpage = None
		self.endpage = None

		self.increased = 0	# how much increased during this step.

	def __str__(self):
		return "pub(%s,%s,%s)" % (self.id , self.title, self.ncitation)

	def report(self):
		return "pub(%s,%s,%s)" % (self.id , self.title, self.ncitation)

# Person
class Person:
	''' Person Model for update citation'''

	def __init__(self, id=0, names=[], pubcount=0):
		self.id = id
		self.names = names
		self.pubcount = pubcount
		self.pubs = None

	def __str__(self):
		return "person(%s:[%s],pubcount:%s)" % (self.id , ','.join(self.names), self.pubcount)

	def loadPubs(self):
		# TODO
		pass

if __name__ == "__main__":
	mpub = ExtractedGoogleScholarResult();
	mpub.id = 1000;
