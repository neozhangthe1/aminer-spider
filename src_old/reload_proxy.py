#!/usr/bin/env python
from com.lish.ajia.proxy.proxyloader import ProxyResource

proxyRes = ProxyResource()
results = proxyRes.load_proxycn()
for model in results:
	print model
proxyRes.saveToFile('/tmp/proxies.txt', results);
