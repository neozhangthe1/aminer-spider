"""
due to some reasons, we need to run a particular setup
to correct some errors about an author.

usage:
1.enter author ID in aminer.org
2.show a list of all papers infor(citations) of that author.
3.show a progress bar
4.show a list of all papers infor(citations) of that author after correction.
5.show difference between before and after.
6.flush to database.
"""
from com.lish.ajia.util.db import DB
from com.lish.ajia.googlescholar.models import Person
from com.lish.pyutil.helper import ExceptionHelper
from com.lish.ajia.googlescholar.extractor import Extractor
from com.lish.ajia.googlescholar.daos import PublicationDao
from com.lish.ajia.googlescholar.pubmatcher import PubMatcher
import MySQLdb

class AuthorUpdater:
    def __init__(self, aid, generation):
        self.aid = aid
        self.generation = generation
        self.person = self.get_author(aid, generation)
        self.pubdao = PublicationDao()
        
    def get_author(self, aid, generation):
        print aid, generation
        self.sql = """select p.id, p.names, pe.pubcount 
            from na_person p left join person_update_ext pe on p.id=pe.id
            where (pe.u_citation_gen is null or pe.u_citation_gen < %s) and p.id=%s
            """ % (generation, aid)
        try:
            conn = DB.pool().getConnection()
            cursor = conn.cursor()
            cursor.execute(self.sql)
            data = cursor.fetchall()
            if cursor.rowcount == 0:
                return
            for aid, names, pubcount in data:
                namelist = [name.strip() for name in names.split(",")]
                print 'get author: ', namelist
                return Person(aid, namelist, pubcount)
            cursor.close()
            conn.close()
        except MySQLdb.Error, e:
            ExceptionHelper.print_exec(e)
            
    def show(self, showlist):
        for x in showlist:
            print x
            
    def update(self):
        pubs = self.pubdao.getPublicationByPerson(self.person.id, self.generation)
        if pubs is not None and len(pubs) == 0:
            self.store.markPersonFinished(self.person)
            print "[*] Mark Person as Finished '%s'." % self.person
            return

        self.show(pubs)
        all_models = Extractor.getInstance().getNodesByPersonName(self.person.names)
        
        print 'all models:'
        for model in all_models:
            print model
        raw_input()
        
        if all_models is not None:
            print "=" * 100
            (pubs_found, pubs_notfound) = PubMatcher.getInstance().matchPub(pubs, all_models)
            if pubs_found is None or pubs_notfound is None:
                print "[ERROR][-/-] person '%s', pubs_found is None or pubs_notfound is None, return"\
                    % self.person
                return
            print "{+A}[%s+%s=%s] Download by page, [found + not_found = total], person '%s'." % (
                len(pubs_found), len(pubs_notfound), len(pubs_found) + len(pubs_notfound), self.person
            )
        else:
            pubs_notfound = pubs
        print 'pubs found :'
        self.show(pubs_found)
        print 'done'
    
if __name__ == '__main__':
    print 'hi'
    aid = (int)(raw_input())
    generation = (int)(raw_input())
    x = AuthorUpdater(aid, generation)
    x.update()
