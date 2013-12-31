scrapers
========

Python Scrapy project used to collect open data on the web, powering our open data catalog.

'''To Run'''
-------------
Requires Python 2.7, Pip and probably virtualenv

``` 
pip install -r requirements.txt
scrapy crawl dayton_local -o ../path/to/data_file.json -t json -s LOG_FILE=../path/to/scrapy.log -s LOG_LEVEL=WARNING
```

