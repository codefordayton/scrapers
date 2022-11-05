. env/bin/activate

echo Cleaning up the directory.
rm delinquent.zip
rm delinquent/*
rm cityreapitems.csv
rm countyreapitems.csv
rm reapitems.csv

echo Starting the scraper.
scrapy runspider dayton/spiders/reap_spider.py -s DOWNLOAD_DELAY=0.05
# python split_reap_items.py

echo Creating the JSON file.
cp reapitems.csv ../daytonreap/
cd ../daytonreap
python scripts/buildjson.py

echo Building the montylots site.
cp georeaps.json ../montylots/_resource/reaps.json
cd ../montylots
npm run build
git add .
git commit -m "Updating the data files."
git push origin main

deactivate
