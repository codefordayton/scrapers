. env/bin/activate

echo Cleaning up the directory.
rm delinquent.zip
rm delinquent/*
rm cityreapitems.csv
rm countyreapitems.csv
rm reapitems.csv

echo Starting the scraper.
scrapy runspider dayton/spiders/reap_spider.py -s DOWNLOAD_DELAY=0.05
python split_reap_items.py

deactivate
