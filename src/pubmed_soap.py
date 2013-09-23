"""
Soap client to fetch articles from Pubmed
"""

from suds.client import Client
eutils_url = 'http://eutils.ncbi.nlm.nih.gov/soap/v2.0/eutils.wsdl'
url = 'http://eutils.ncbi.nlm.nih.gov/soap/v2.0/efetch_pubmed.wsdl'
client_eu = Client(eutils_url)
client = Client(url)

#print client

#print client_eu
sres = client_eu.service.run_eSearch(db='pubmed', term="Dengue")
print sres
#result = client.service.run_eFetch(query_key="Dengue")
#print result
