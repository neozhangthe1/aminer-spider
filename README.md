scrapy-linkedin
===============

Using Scrapy to get Linkedin's person public profile.

### feature
* Get all **public** profile
* Using Scrapy
* Enable auto throttle
* Enable naive proxy providing
* Agent rotating
* Support Unicode
* Using MongoDB as Backend
* ...

### todo
* **Improve speed**
* **Improve availablity**
* add ajax load support
* more complex proxy providing algorithm


### Dependency
* Scrapy == 0.16
* pymongo 
* BeautifulSoup, UnicodeDammit


### usage
	1. start a MongoDB instance, `mongod`
	2. run the crawler, `scrapy crawl LinkedinSpider`

you may found `Rakefile` helpful.


### configuration
you can change MongoDB setting ang other things in `settings.py`. 

### note
if you just need whatever public profiles, there are better ways to do it. 
check out these urls: http://www.linkedin.com/directory/people/[a-z].html

Our strategy is following `also-view` links in public profile.
