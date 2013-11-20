#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#class a:
#	def __init__(self):
#		self.pubmap = {}
#		self.pubmap[1] = Publication(1, 1, "title1", "1", "1", "333", 3)
#		self.pubmap[2] = Publication(2, 1, "title2", "1", "1", "333", 3)
#		self.pubmap[3] = Publication(3, 1, "title3", "1", "1", "333", 3)
#		self.pubmap[4] = Publication(4, 1, "title4", "1", "1", "333", 3)
#
#	def doit(self):
#		done = False
#		pub_ids = [1, 2, 3, 4]
#		person_name = "jie tang"
#		# try pin url
#
#		author_str = " author:\"%s\"" % person_name
#		pieces = ["allintitle:"]
#
#		total_length = 11 + len(author_str)
#
#		#"".join(["a","b"])
#		pubs_in_url = []
#		while len(pub_ids) > 0:
#			print len(pub_ids)
#			pub_id = pub_ids.pop()
#			if pub_id in self.pubmap:			# avoid dup
#				pub = self.pubmap[pub_id]
#
#				# test bound
#				if len(pubs_in_url) == 0:
#					total_length += 2 #len("\"\"")
#				elif len(pubs_in_url) > 0:
#					total_length += 6 #len(" OR \"\"")
#				total_length += len(pub.title)
#
#				if total_length > 50: # outof boundary
#					pub_ids.append(pub_id) # add pubs back
#					break
#
#				# proceed
#				del self.pubmap[pub_id] # delete pub.
#				if len(pubs_in_url) == 0:
#					pieces.append("\"%s\"" % pub.title)
#				elif len(pubs_in_url) > 0:
#					pieces.append(" OR \"%s\"" % pub.title)
#				pubs_in_url.append(pub)
#
#		if len(pubs_in_url) > 0:
#			pieces.append(author_str)
#			url = "".join(pieces)
#			return url, pubs_in_url
#		else:
#			return None, None
#
#if __name__ == "__main__":
#	#print datetime.datetime.tzinfo
#	
#	d = datetime.datetime.now()
#	print d
#	time.sleep(67)
#	d2 = datetime.datetime.now() - d
#	print d2
#	print d2.microseconds
#	print d2.seconds
#	print d2.days
#	
#	
#	
#	sys.exit();
#	#print a().doit()
#	sss = '''<a href="http://portal.acm.org/citation.cfm?id=1281309" onmousedown="return clk(this.href,'','res','0')"><b>Truth discovery with multiple conflicting information providers on the web</b></a></h3> - <span class=a>&#x25ba;</span><b class=fl><a href="http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.89.8378&amp;rep=rep1&amp;type=pdf" onmousedown="return clk(this.href,'gga','gga','0')">psu.edu</a> <font size=-2 class=f>[PDF]</font>&nbsp;</b><font size=-1><br><span class="a">X Yin, J Han, PS Yu - Proceedings of the 13th ACM SIGKDD international  &hellip;, 2007 - portal.acm.org</span><br>Page 1. Truth Discovery with Multiple Conflicting Information Providers on the Web ∗<br>
#Xiaoxin Yin ∗ UIUC xyin1@uiuc.edu Jiawei Han UIUC hanj@cs.uiuc.edu <b>...</b> 
#<br><span class=fl><a href="/scholar?cites=1172281283877955576&amp;hl=en&amp;num=100">Cited by 16</a> - <a href="/scholar?q=related:-Gdi3p3HRBAJ:scholar.google.com/&amp;hl=en&amp;num=100">Related articles</a> - <a href="/scholar?cluster=1172281283877955576&amp;hl=en&amp;num=100">All 16 versions</a></span></font>  <p>
#'''
#	re_citedby = re.compile("<span class=fl>(<a( .+)? href=\".+\".+?>)?Cited by (\d+)(</a>)?", re.I)
#	re_citedby = re.compile("<span class=fl>(<a[^>]+?>)?Cited by (\d+)(</a>)?", re.I)
#	print "haha"
#	match_citedby = re_citedby.search(sss)
#	if match_citedby is not None:
#		print "find citation %s" % match_citedby.group(2)
#
#
#
#
import urllib2

#######################################################
if __name__ == '__main__':
#	print test_proxyget('http://www.google.com')
#	l_proxy_info = {
#	'user' : 'keg',
#	'pass' : 'keg2007',
#	'host' : '166.111.68.67',
#	'port' : 3128
#	}
#	
#	l_proxy_support = urllib2.ProxyHandler({"http" : \
#		"http://%(user)s:%(pass)s@%(host)s:%(port)d" %
#		l_proxy_info})
#	l_opener = urllib2.build_opener(l_proxy_support, urllib2.HTTPHandler)
#	
#	urllib2.install_opener(l_opener)
#	l_req = urllib2.urlopen('http://www.baidu.com/')
#	print l_req.headers
#	print l_req.read()

	
	l_proxy_info = {
	'host' : '219.94.142.25',
	'port' : 80
	}
	
	l_proxy_support = urllib2.ProxyHandler({"http" : \
		"http://%(host)s:%(port)d" %
		l_proxy_info})
	l_opener = urllib2.build_opener(l_proxy_support, urllib2.HTTPHandler)
	
	urllib2.install_opener(l_opener)
	l_req = urllib2.urlopen('http://www.baidu.com/')
	print l_req.headers
	print l_req.read()
