Code For Dayton Web Scrapers
============================

This project collects data from various City of Dayton area websites to power our open data catalog.

'''To Run'''
-------------
Requires Python 2.7, Pip and probably virtualenv.

Installation
===================
``` 
pip install -r requirements.txt
scrapy crawl spider_name
```

You can view the available spiders by running
```scrapy list```

Scraped data is output as JSON in 'feed.json'


Vagrant
=======
First, install Vagrant for your host operating system. Vagrant runs virtual machines inside VirtualBox on your host OS. We use
a common image and configure it using Vagrant (Puppet) so that all developers have the same runtime environment.
```vagrant box add precise32 http://files.vagrantup.com/precise32.box```
