# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from time import time
import urllib2
from urllib2 import HTTPError
from pymongo import Connection
import gridfs
from gridfs.errors import FileExists, GridFSError
import md5
import settings


class ScholarPipeline(object):
    def save_document(self, item):
#        download_dir = '/tmp/pdfs/'
        if item['URL']:
            pdf_url = None
            html_url = None
            url = item['URL']
            if url.endswith('.pdf'):
                pdf_url = item['URL']
            else:
                html_url = item['URL']
                # Download the article
            timestamp = str(time())
            fid = None
            if pdf_url:
                try:
                    f = urllib2.urlopen(pdf_url, timeout=15)
                    item['Filename'] = timestamp + '.pdf' if not item['Bibtex'] else item['Bibtex'].split(',')[0].split('{')[-1].strip() + '.pdf'
                    item['Mimetype'] = 'application/pdf'
                    fid = self.save_to_gridfs(f, item)
                except HTTPError as error:
                    print "Download of file %s failed with %s" % (item['URL'], error)
            if html_url:
                try:
                    f = urllib2.urlopen(html_url, timeout=15)
                    item['Filename'] = timestamp + '.html' if not item['Bibtex'] else item['Bibtex'].split(',')[0].split('{')[-1].strip()+ '.html'
                    item['Mimetype'] = 'text/html'
                    fid = self.save_to_gridfs(f, item)
                except HTTPError as error:
                    print "Download of file %s failed with %s" % (item['URL'], error)
            item['Fileid'] = fid
        else:
            item['Fileid'] = None
            item['Filename'] = None
            item['Mimetype'] = None

    def save_to_gridfs(self, fobj, item):
        """
        Save reference file to gridfs.
        md5 hash will be used as _id to avoid stroing of identical files
        """
        duplicates = list(self.collection.find({'Bibtex': item['Bibtex']}))
        if duplicates:
            #Don't save file is a duplicate entry has already been processed
            return
        fs = gridfs.GridFS(self.db)
        content = fobj.read()
        h = md5.md5(content)
        try:
            fid = fs.put(data=content,
                        _id=h.hexdigest(),
                        filename=item['Filename'],
                        contentType=item['Mimetype'])
        except FileExists:
            print "File %s has already been Stored, returning stored ID."%item['Filename']
            fid = h.hexdigest()
        except GridFSError as err:
            print err, item['Filename']
            fid = None
        return fid

    def process_item(self, item, spider):
        self.save_document(item)
        return item

    def open_spider(self, spider):
        self.db = Connection('166.111.134.53', 12345)[settings.MONGO_DATABASE]
        self.collection = self.db['_'.join(spider.terms)]


class MongoDBPipeline(object):
    """
    Saves the item to a mongoDB database and collection
    and updates the Search stats collection
    """
    def process_item(self, item, spider):
        duplicates = list(self.collection.find({'Bibtex': item['Bibtex']}))

        if not duplicates:
            # check if item has already been inserted
            self.collection.insert(dict(item))
            self.update_stats(spider)
        return item

    def update_stats(self,spider):
        """
        updates search stats
        """
        search_stats = self.searchcol.find_one({"namecollection":self.collection.name})
        if search_stats != None:
            us = search_stats['years']
            c = us.get(str(spider.ylo),0)
            us[str(spider.ylo)] = c+1
            self.searchcol.update({"namecollection":self.collection.name},{'$set':{'years':us}})
        else:
            #create an entry of one item for this year
            self.searchcol.insert({"namecollection":self.collection.name,"years":{str(spider.ylo):1}})

    def open_spider(self, spider):
        db = Connection('166.111.134.53', 12345)[settings.MONGO_DATABASE]
        self.collection = db['_'.join(spider.terms)]
        self.searchcol = db['Searches']

    def close_spider(self, spider):
        pass
