scrapers
========

Python Scrapy project used to collect open data on the web, powering our open data catalog.

'''To Run'''
-------------
Requires Python 2.7, Pip and probably virtualenv. To install Scrapy on Windows, per [a Stackoverflow question](http://stackoverflow.com/questions/9151268/installing-scrapy-pyopenssl-in-windows-virtualenv),
 you will also need to install [the full version of OpenSSL ](http://slproweb.com/products/Win32OpenSSL.html).

Installation
===================
``` 
pip install -r requirements.txt
scrapy crawl spider_name
```

You can view the available spiders by running
```scrapy list```

Scraped data is output as JSON in 'feed.json'
