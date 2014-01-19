scrapers
========

Python Scrapy project used to collect open data on the web, powering our open data catalog.

'''To Run'''
-------------
Requires Python 2.7, Pip and probably virtualenv

Installation
===================
``` 
pip install -r requirements.txt
scrapy crawl spider_name
```

You can view the available spiders by running
```scrapy list```

Scraped data is output as JSON in 'feed.json'
