from scrapy import log
from proxy import PROXIES
from agents import AGENTS

import random

"""
Custom proxy provider. 
"""
class CustomHttpProxyMiddleware(object):
    
    def process_request(self, request, spider):
        # TODO implement complex proxy providing algorithm
        if self.use_proxy(request):
            p = '222.124.147.105:8080'
            #'120.35.31.101:8080'
            try:
                request.meta['proxy'] = "http://%s" % p['ip_port']
            except Exception, e:
                log.msg("Exception %s" % e, _level=log.CRITICAL)
                
    
    def use_proxy(self, request):
        """
        using direct download for depth <= 2
        using proxy with probability 0.3
        """
        if "depth" in request.meta and int(request.meta['depth']) <= 2:
            return False
        i = random.randint(1, 10)
        return i <= 2
    
    
"""
change request header nealy every time
"""
class CustomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        agent = random.choice(AGENTS)
        request.headers['User-Agent'] = agent


# Importing base64 library because we'll need it ONLY in case if the proxy we are going to use requires authentication
import base64
 
# Start your middleware class

