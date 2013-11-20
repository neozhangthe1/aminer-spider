from scrapy.spider import BaseSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request 
from scholar.items import ScholarItem
from bs4 import BeautifulSoup
import re
import os
import urllib2, cookielib
import string, random
from itertools import cycle
from pymongo import Connection
import datetime
from scholar import settings

os.environ['http_proxy'] = "http://127.0.0.1:8118"

class ScholarSpider(BaseSpider):
    name = "gscholar"
    allowed_domains = ["scholar.google.com", "scholar.google.com.br"]
    num = 100
    terms = ['Dengue',"model"]
    # Cycle over many many user-agent-strings
    user_agents = cycle(['Mozilla/5.0 (X11; U; SunOS sun4u; en-US; rv:1.7.7) Gecko/20050421',
                         'Mozilla/5.0 (X11; Linux x86_64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1',
                    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.7) Gecko/20050427 Red Hat/1.7.7-1.1.3.4',
                    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.7) Gecko/20050420 Debian/1.7.7-2',
                    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.7) Gecko/20050414',
                    'Mozilla/5.0 (X11; U; Linux i686; de-AT; rv:1.7.7) Gecko/20050415',
                    'Mozilla/5.0 (Windows; U; Windows NT 5.1; fr-FR; rv:1.7.7) Gecko/20050414',
                    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.7) Gecko/20050414',
                    'Mozilla/5.0 (Windows; U; Windows NT 5.1; de-AT; rv:1.7.7) Gecko/20050414',
                    'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.7.7) Gecko/20050414',
                    'Mozilla/5.0 (Windows; U; Windows NT 5.0; de-AT; rv:1.7.7) Gecko/20050414'])
    # generate a random id for the scholar cookie: e.g.: '97a41fcd26d76ae7'
    id = lambda x:''.join(random.sample(string.hexdigits,16)).lower()
    #TODO: add a maximum number of refs to be fetched.

    
    def start_requests(self):
        self.ylo, self.yhi, self.start = self.get_time_range(self.terms)
        return [Request("http://scholar.google.com.br/scholar?start="+str(self.start)+"&q="+'+'.join(self.terms)+\
                        "&num="+str(self.num)+"&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=&as_publication=&as_ylo="+\
                        str(self.ylo)+"&as_yhi="+str(self.yhi)+"&as_sdt=1.&as_sdtp=on&as_sdtf=&as_sdts=5&btnG=Search+Scholar&hl=en",
                cookies={'GSP':'ID=%s:CF=4'%self.id()},meta={'proxy':'http://127.0.0.1:8118','User-agent':self.user_agents.next()})]

    def get_next_request(self,soup,previousurl):
        """
        Check if we are not in the last page of results
        and return request object.
        otherwise return none
        """
        res = soup.findAll('span',attrs={'class':'SPRITE_nav_next'})
        if res == []:
            # if we are in the last page of results, start fetching from previous year
            self.ylo, self.yhi, self.start = self.get_time_range(self.terms,True)
        else:
            self.ylo, self.yhi, self.start = self.get_time_range(self.terms)
        self.num += 100
        nxt_url = previousurl.replace(r'\?start=d+', '?start=%s&'%self.num)
        nxt_url = re.sub(r'&as_ylo=\d\d\d\d','&as_ylo=%s'%self.ylo ,nxt_url)
        nxt_url = re.sub(r'&as_yhi=\d\d\d\d','&as_yhi=%s'%self.yhi ,nxt_url)
        req = Request(nxt_url,cookies={'GSP':'ID=%s:CF=4'%self.id()},
                      meta={'proxy':'http://127.0.0.1:8118',
                            'User-agent':self.user_agents.next()})
        return req

    def get_time_range(self, terms, getprevious=False):
        """
        Check the records already downloaded in the database
        returns year,year,starting_record
        """
        currentYear = datetime.date.today().year
        col = "_".join(terms)
        db = Connection('166.111.134.53', 12345)[settings.MONGO_DATABASE]
        #db = Connection('10.1.1.111', 12345)[settings.MONGO_DATABASE]
        coll = db[col]
        num_fetched = coll.count()
        searchCol = db['Searches']
        data = list(searchCol.find({"namecollection":col}))
        if not data:
            # there are no records of this search
            print "First time searching for %s starting with %s"%(col,currentYear)
            return currentYear,currentYear,num_fetched
        else:
#            start fetching from the count of references in db. not guaranteed to not skip articles but is good enough.
            years = data[0]['years']
            ylo = int(sorted(years.keys(),reverse=True)[0])
            if getprevious:
                ylo -= 1
            return ylo,ylo,num_fetched


    def fetch_bibtex(self,biburl):
        """
        Makes an additional request to fetch the bibtex record
        """
        user_agent = self.user_agents.next()
        proxy_support = urllib2.ProxyHandler({"http" : "http://127.0.0.1:8118"})
        opener = urllib2.build_opener(proxy_support)
        opener.addheaders = [('User-agent', user_agent)] #maybe use this to use tor

        req = urllib2.Request(biburl)
        req.add_header('User-Agent',user_agent)
        cj = cookielib.CookieJar()
        ck = cookielib.Cookie(name='GSP',value='ID=97a41fdc26d76ae7:CF=4',port=None,comment='',path='',expires=None,secure=False,discard=False,comment_url=None,domain='scholar.google.com.br',domain_initial_dot=False,domain_specified=True,path_specified=False,port_specified=False,rest='',version=None)
        cj.set_cookie(ck)
        cj.add_cookie_header(req)
        try:
#            response = urllib2.urlopen(req,timeout=15)
            response = opener.open(req,timeout=15)
        except urllib2.URLError:
            return ""
        return response.read()

    def parse_bibtex(self,rec):
        """
        Simple parser to extract some basic fields from bibtex record
        """
        data = {}
        for f in rec.split('},'):
            if "=" not in f: continue
            data[f.split('=')[0].strip()] = f.split('=')[1].strip().strip('{}')
        if 'year' in data:
            data['year'] = int(data['year'].strip().strip('{}'))
#        print data
        return data
        

    def parse(self, response):
        filename = response.url.split("/")[-2]
        open(filename, 'wb').write(response.body)
        soup = BeautifulSoup(response.body)
        citations = 0
        results = []
        limit = 10
        #print "==========> ", soup.findAll('a')[-10:]
        for record in soup.findAll('div', attrs= {'class':'gs_r'}):
#            print record.findAll(text="[CITATION]")
            if record.findAll(text="[CITATION]") : 
                continue #Skip citation items
                citations +=1
            # Included error checking
            topPart = record.first('div', {'class': 'gs_rt'})
            # Clean up the URL, make sure it does not contain '\' but '/' instead

            pubTitle = ""
            try:
                for part in topPart.a.contents:
                    pubTitle += str(part)
            except AttributeError:
                continue # citation items don't have title in <a></a> and are not scraped
#            print "==> URL: ", pubURL
#            print "==> Title: ",  pubTitle
            if pubTitle == "":
                match1 = re.findall('<b>\[CITATION\]<\/b><\/font>(.*)- <a',str(record))
                match2 = re.split('- <a',match1[citations])
                pubTitle = re.sub('<\/?(\S)+>',"",match2[0])
                citations = citations + 1
                
            # Get PDF if available
            pubURL = ""
            for u in record.findAll('span', {'class':'gs_ggs gs_fl'}):
                url = u.a['href']
                pubURL = url
                #downloads done in the item pipeline
           
            authorPart = record.findAll('span', {'class': 'gs_a'})[0].string
            if str(authorPart)=='Null': 
                authorPart = ''
                # Sometimes even BeautifulSoup can fail, fall back to regex
                m = re.findall('<font size="-1">(.*)</font>', str(record))
                if len(m)>0:
                    authorPart = m[0]

#            print "==> Authors: ", authorPart
            # Assume that the fields are delimited by ' - ', the first entry will be the
            # list of authors, the last entry is the journal URL, anything in between
            # should be the journal year
            try:
                idx_start = authorPart.find(' - ')
                idx_end = authorPart.rfind(' - ')
                pubAuthors = authorPart[:idx_start]             
                pubJournalYear = authorPart[idx_start + 3:idx_end]
                publisher = authorPart[idx_end + 3:]
            except AttributeError:
                #TODO: add a logging entry for this error
                pubAuthors = ''
                pubJournalYear = ''
                publisher = ''
            # If (only one ' - ' is found) and (the end bit contains '\d\d\d\d')
            # then the last bit is journal year instead of journal URL
            Year = None
            if pubJournalYear=='' and re.search(r'\d\d\d\d', publisher)!=None:
                pubJournalYear = publisher
                try:
                    Year = int(pubJournalYear.split(',')[1])
                except ValueError:
                    pass
                publisher = ''
                           
            pubAbstract = ""
            match = re.search(r"Cited by ([^<]*)", str(record))
            pubCitation = ''
            if match != None:
                pubCitation = match.group(1)
                try:
                    pubCitation = int(pubCitation)
                except ValueError:
                    pass
                
            #Get the Bibtex entry
            bibtex_tags = record.findAll("a",{'href':re.compile(r'/scholar\.bib\?')})
            if bibtex_tags:
                biburl = 'http://scholar.google.com.br'+bibtex_tags[0]['href']
                bibtex = self.fetch_bibtex(biburl)
                bibdata = self.parse_bibtex(bibtex)
#                print "======> ",bibtex
#                print "====>", bibdata
            else:
                bibtex = ""
                bibdata = {}

            itemdict = {
                "URL": pubURL,
                "Title": bibdata.get('title',pubTitle),
                "Authors": bibdata.get('author', pubAuthors.strip('&hellip;')),
                "Journal": bibdata.get('journal',pubJournalYear.split(',')[0].strip('&hellip;')),
                "Year": bibdata.get('year',Year),
                "Publisher": bibdata.get('publisher',publisher),
                "Abstract": pubAbstract,
                "NumCited": pubCitation,
                "Terms": self.terms,
                "Bibtex":bibtex
            }
            it = ScholarItem()
            it.update(itemdict)
            yield it
        prv_url = response.url#check this
        req = self.get_next_request(soup,prv_url)

        print '===============> ', self.num
        
        yield req
#            results.append(it)
#        print results
#        return results
    

