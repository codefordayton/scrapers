# If `env/bin/python` exists, it is used. If not, use PATH to find python.
SYSTEM_PYTHON  = $(or $(shell which python3), $(shell which python))
PYTHON         = $(or $(wildcard env/bin/python), $(SYSTEM_PYTHON))

.PHONY: scrape

clean:
	echo Cleaning up the directory.
	rm delinquent.zip
	rm delinquent/*
	rm cityreapitems.csv
	rm countyreapitems.csv
	rm reapitems.csv

scrape:
	@echo Starting the scraper.
	# scrapy runspider dayton/spiders/reap_spider.py -s DOWNLOAD_DELAY=0.05
	# # python scripts/split_reap_items.py

build:
	$(PYTHON) scripts/buildjson.py

update_shapes:
	@echo Cleaning up the directory.
	rm -rf shapefiles
	rm shapefiles.zip
	@echo Downloading shapefiles.
	curl -o shapefiles.zip http://www.mcauditor.org/downloads/Shape_files/SHAPEFILES_PARCELLINES_ROW_OLDLOT.zip
	@echo Unzipping the files.
	unzip shapefiles.zip -d shapefiles

	@echo Converting to WGS-1984.
	ogr2ogr -t_srs EPSG:4326 data/Parcels.shp shapefiles/Parcel.shp

	@echo Create the parcel centroid
	$(PYTHON) scripts/init_parcel_centroid.py data/Parcels.shp

