# -*- coding: utf-8 -*-
'''
Runner Platform Module: DB
KEG • elivoa@gmail.com
Time-stamp: "root 2009/07/24 13:04:13"
'''

#from runner.proxy import proxy
from comm import db
from google_citation.DataWalker import PersonWalker, PublicationWalker
from google_citation.dbs import dbs, Author2PubDao, PersonDao
from runner.DB import DB
import MySQLdb
import sys
from google_citation.dbs import dbs, PublicationDao

#######################################################
# Self Test 
#######################################################
pubdao = PublicationDao()

def export(jconf_id, jconf_name, outputfile):
	pubs = pubdao.getPublicationByConf(jconf_id);
	print "#%s" % jconf_name
	outputfile.write("#%s\n" % jconf_name)
	for pub in pubs:
		strs = []
		strs.append("title=")
		strs.append(pub.title)
		strs.append("\tyear=")
		strs.append(str(pub.year))
		strs.append("\tauthors=")
		strs.append(pub.authors)
		strs.append("\tstartpage=")
		strs.append(str(pub.startpage))
		strs.append("\tendpage=")
		strs.append(str(pub.endpage))
		
		str_out = "".join(strs)
		outputfile.write(str_out)
		outputfile.write("\n")

if __name__ == '__main__':
	desc = ''' 
	export Some info. listed below as a reminder.
		database conf.
		icde,1935
		sigmod,3499
		vldb,3771
		
		data mining conf.
		icdm,1938
		kdd,2651
		cikm,710
	'''
	f = file("icde-sigmod-vldb.txt", "w")
	export(1935, "icde", f)
	export(3499, "sigmod", f)
	export(3771, "vldb", f)

	f = file("icdm-kdd-cikm.txt", "w")
	export(1938, "icdm", f)
	export(2651, "kdd", f)
	export(710, "cikm", f)
	print "====== print out ======"




	print "====== Program Finished ======"






