import dbm
import csv
import json
from datetime import datetime

db = dbm.open('./centroids.dbm', 'r')
#open output json file
file = open('georeaps.json', 'w')
values = []
with open('reapitems.csv') as csvfile:
    reader = csv.DictReader(csvfile, ['parcel', 'street', 'eligible', 'paymentplan', 'lastyear', 'paymentwindow'])
    for row in reader:
        #if the record should be included, include it
        if row['eligible'] != 'Sold' and row['paymentplan'] == 'False' and row['paymentwindow'] == 'False' and row['lastyear'] < '2012':
            try:
                latlon = db[row['parcel']].split()
                values.append({'parcelid': row['parcel'], 'street': row['street'], 'lat': latlon[0], 'lon': latlon[1]})
            except:
                #if not, log it in a separate json file for analysis/reporting
                print row['parcel']
    file.write('var lastupdated = new Date("' + datetime.now().strftime("%B %d, %Y %H:%M:%S") + '");\n')
    file.write('var points =')
    file.write(json.dumps(values, indent=2))
    file.write(';')
    file.close()
