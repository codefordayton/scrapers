. env/bin/activate

echo Cleaning up the directory.
rm -rf shapefiles
rm shapefiles.zip
mkdir data

echo Downloading shapefiles.
curl -o shapefiles.zip http://www.mcauditor.org/downloads/Shape_files/SHAPEFILE_PARCELLINES_ROW_OLDLOT.ZIP

echo Unzipping the files.
unzip shapefiles.zip -d shapefiles

echo Converting to WGS-1984.
ogr2ogr -t_srs EPSG:4326 data/Parcels.shp shapefiles/Parcel.shp

echo Create the parcel centroid
python init_parcel_centroid.py data/Parcels.shp

deactivate
