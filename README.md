Code For Dayton Web Scrapers
============================

This project collects data from various City of Dayton area websites to power our open data catalog.

Installation
===================
The application runs in a Python 3.x virtualenv. To create a python virtualenv, run:

`virtualenv env -ppython3`

After creating the virtual environment, activate it with:

`. env/bin/activate`

All commands after this assume you are inside the virtual environment for the project you are working on.

Dependencies for the projects can be installed via:

`pip install -r requirements.txt`

The `requirements.txt` file contains all the packages that the project depends upon. New requirements should be added to this file, either manually or by running `pip freeze > requirements.txt`.

Crawling
===================
Spiders crawl a website, extracting data from the web pages. Each spider is customized for a specific website or set of websites.
You can view the available spiders by running
```scrapy list```

You can start the crawling using the below command:
```
scrapy crawl spider_name
```

Scraped data is output as JSON in 'feed.json'
