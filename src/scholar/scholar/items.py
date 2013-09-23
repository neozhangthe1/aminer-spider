# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class ScholarItem(Item):
    """
    Define the fields for each item to be scraped from google scholar
    """
    URL = Field()       # link to the article
    Title = Field()     # title of the publication
    Authors = Field()   # authors (example: DF Easton, DT Bishop, D Ford)
    Journal= Field()   # journal name & year (example: Nature)
    Year = Field()
    Publisher = Field()    # journal Publisher 
    Abstract = Field()  # abstract of the publication
    NumCited   = Field() # number of times the publication is cited
    Terms = Field()     # list of search terms used in the query
    Bibtex = Field() #Bibtex entry for this item
    Fileid = Field() # file id of the article stored in mongodb gridfs
    Filename = Field() # file name in gridfs
    Mimetype = Field() # Mimetype of the article file

class PubmedItem(Item):
    """
    Define the fields for each item to be scraped from pubmed
    """
    URL = Field()       # link to the article
    Title = Field()     # title of the publication
    Authors = Field()   # authors (example: DF Easton, DT Bishop, D Ford)
    JournalYear= Field()   # journal name & year (example: Nature, 2001)
    JournalURL = Field()    # link to the journal main website (example: www.nature.com)
    Abstract = Field()  # abstract of the publication
    NumCited   = Field() # number of times the publication is cited
    Terms = Field()     # list of search terms used in the query
