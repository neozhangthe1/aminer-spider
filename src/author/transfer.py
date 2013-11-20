import MySQLdb
import pymongo
import re
import editdist
import os
from PriorityPeople import PriorityPeople
import time




class matching:

	def __init__(self):
		self.conn_mon = pymongo.Connection(host='10.1.1.111',port=12345)
		self.conn_my = MySQLdb.connect(host='10.1.1.110',user='root',passwd='keg2012',db='arnet_db')
		self.db_mon = self.conn_mon['arnet_db']
		self.table_mon='pubication_test_3rd'

	def findpublication8name(self,aid):

		'''
		returns a list like:[['title1','title2'],id]
		'''
		
		cursor_my = self.conn_my.cursor()#mysql cursor

		if type(aid) is not list:
			cursor_my.execute('select pid from na_author2pub where aid = "%s"'%aid)
			pid = cursor_my.fetchall()
			pidList=[]
			for perid in pid:
				pidList.append(perid[0])

		else:
			pass
		paperList=[]
		for perid in pid:
			cursor_my.execute('select title,ncitation from publication where id = %d'%perid)
			title = cursor_my.fetchall()
			if len(title) >=1:
			  title = title[0]
			  title = {'title':title[0],'ncitation':title[1],'pid':perid}
			  paperList.append(title)
			else:
				continue
			#print title

		return [paperList,aid]




	def getpList(self,aid):

		'''
		returns a list contain paper info dic like [{title,citation,essay_others}{title,citation,essay_others}]
		'''
		table_mon = self.db_mon[self.table_mon]
		if table_mon.find_one({'_id':aid}) is None:
			return None
		paperList = table_mon.find_one({'_id':aid}).get('paper')
		contentList = []
		for paper in paperList:
			citation = paper['citation']
			title = paper['title']
			essay_others = paper['essay_others']
			contentList.append({'title':title,'citation':citation,'essay_others':essay_others})

		return contentList
	

	def matchPub(self, golist, mylist,aid):
		data = []
		fdr=open('./output/data.txt','r')
		for i in fdr.readlines():
			data.append(i)
		fdr.close()
		cursor_my = self.conn_my.cursor()
		print 'matching'
		'''
		automatically updates the database
		return a list of paper dics containing updating information
		'''
		table_mon = self.db_mon[self.table_mon]
		
		godics = golist
		mytitles = mylist[0]		
		aid = mylist[1]
		print_not_matched = False
		pubs_matched = []
		pubs_not_matched = []
		#fw1 = open('C:\\Python27\\tutorial\\tutorial\\test\\%dmatched.txt'%aid,'w')
		#fw2 = open('C:\\Python27\\tutorial\\tutorial\\test\\%dfailed.txt'%aid,'w')
		fw3 = open('./output/%dmulmatched.txt'%aid,'w')
		t = 0



		for mydic in mytitles:
			ncitation = mydic['ncitation']
			mytitle = mydic['title']
			mytitleCleaned = self.cleanGoogleTitle(mytitle)
			short_key = mytitleCleaned[1]		
			matchedlist = []
			pid = mydic['pid']
			pid = pid[0]	
			for godic in godics:
				start = time.time()		
				gotitle = godic['title']
				_gotitle = ''
				for cha in gotitle:
					if cha <= chr(127):
						_gotitle= _gotitle+cha
				gotitleCleaned = self.cleanGoogleTitle(gotitle)
				key_title = gotitleCleaned[1]
				has_dot = gotitleCleaned[2]				
				exactmatched = False				
				if has_dot:
					
					if key_title.find(short_key) != -1:
						exactmatched = True
						matchedlist.append(godic)
						godics.remove(godic)
				
				else:
					
					if key_title == short_key:
						exactmatched = True
						matchedlist.append(godic)
						godics.remove(godic)

				if not exactmatched:#if can not be critical matched, try by calculate Levenshtein distance
					ed = editdist.distance(short_key, key_title)
					
					if ed < 10:#adaptable
						looseValue = float(len(key_title)) * (10 / float(100))
						
						if looseValue > ed:
							matchedlist.append(godic)
							godics.remove(godic)
				end = time.time()
				if (start - end) != 0:
					t+=1




			if len(matchedlist) == 1:

				try:
				  pubs_matched.append({'title':matchedlist[0]['title'],'pid_in_mysql':pid,'citation':matchedlist[0]['citation'],'essay_others':godic['essay_others']})
				  #fw1.write('title1:%s title2:%s citation:%s ncitation:%s pid%d\n'%(mytitle,matchedlist[0]['title'],matchedlist[0]['citation'],ncitation,pid[0]))
				except:
					pass
				  #fw1.write('title1:%s citation:%s ncitation:%s pid%d\n'%(mytitle,matchedlist[0]['citation'],ncitation,pid[0]))
			elif len(matchedlist) >=2:
				same = False
				num = len(matchedlist)
				for i in range(0,num):
					if i == num - 1:
						same = True
						break
					if matchedlist[i] == matchedlist[i+1]:
						continue
					else:
						break
				if same:
				  try:
				    pubs_matched.append({'title':matchedlist[0]['title'],'pid_in_mysql':pid,'citation':matchedlist[0]['citation'],'essay_others':godic['essay_others']})  
				  except:
				  	pass

				else:
					for paper in matchedlist:
						godics.append(paper)
						fw3.write('title1:%s citation:%s ncitation:%s pid%d\n'%(mytitle,matchedlist[0]['citation'],ncitation,pid))


			else:
				#fw2.write('title:%s citation:-1\n'%mytitle)
				#pubs_not_matched.append({'title':matchedlist[0]['title'],'citation':matchedlist[0]['citation'],'essay_others':godic['essay_others']})
				continue
		#fw1.close()
		#fw2.close()
		fw3.close()
		fdw = open('./output/data.txt','w')
		log = '%d %d %d %f %d \n'%(aid,len(pubs_matched),len(mytitles),float(len(pubs_matched))/float(len(mytitles)),t)
		print log
		data.append(log)
		for i in data:
			fdw.write(i)
		fdw.close()
		pubs_matched.extend(godics)
		return pubs_matched

	def cleanGoogleTitle(self,title):
		'''
		return a list containing 3 element
		'''
		has_dot = False
		titleCleaned = title
		

        # clean step 1
		titleCleaned = re.sub("(<(.*?)>)", "", titleCleaned)
        # if has dot
		re_hasdot = re.compile(".", re.I)
		match = re_hasdot.search(title)
		if match is not None:
			has_dot = True
        # clean step 2, here title is readable
		titleCleaned = re.sub("(&nbsp;|&#x25ba;|&hellip;)", "", titleCleaned)
		titleCleaned = re.sub("(&#.+?;|&.+?;)", "", titleCleaned)
		titleCleaned = titleCleaned.strip()
		readableTitle = titleCleaned

        # Shrink, only letters left
		titleCleaned = re.sub("\W", "", titleCleaned)
		titleCleaned = titleCleaned.lower()
		return (readableTitle, titleCleaned, has_dot)
	
	def matcher(self, aid):#interface
		'''
		author is str, must be exactly matched with the name in na_person
		'''
		table_mon = self.db_mon[self.table_mon]
		golist = self.getpList(aid)
		mylist = self.findpublication8name(aid)
		if golist is not None:
			pubs_matched = self.matchPub(golist,mylist,aid)
			table_mon.update({'_id':aid},{"$set":{'paper':pubs_matched}})

        
	



if __name__ == "__main__":
	print "start"
	a = matching()
	i=1
	while True:
		if i == 39591:
			i = 0
			continue
		else:
			aid = PriorityPeople[i]
			print "current person", aid
			table_mon = a.db_mon[a.table_mon]
			paperList = table_mon.find_one({'_id':aid}).get('paper')
			if len(paperList) > 10000:
				i+=1
				continue
			else:
				# a.matcher(aid)
				try:
					a.matcher(aid)
				except:
					i+=1
					continue
				else:
					i+=1
					continue
			#try:
			#	a.matcher(aid)
			#except:
			#	continue


	#for i in range()

	#i = 100
	#while i <= 3000:
	#	aid = PriorityPeople[i]
	#	a = matching()
	#	a.matcher(aid)
	#	i +=1



	