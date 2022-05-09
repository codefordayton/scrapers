import dbm
import csv
import json
import traceback
from datetime import datetime

def is_eligible(row):
    return (row['eligible'] != 'Sold' and row['paymentplan'] == 'False' and
            row['paymentwindow'] == 'False' and row['lastyear'] < '2018' and
            row['class'] == 'R')


def is_new(parcel_id, old_rows):
    for old_row in old_rows:
        old_id = old_row.get('parcelid', '').replace(' ', '')
        if old_id == parcel_id:
            return False
    return True


def get_city(record):
    return "".join( chr(x) for x in b' '.join(record[2:]))

def get_lat(record):
    return "".join( chr(x) for x in record[0])

def get_lon(record):
    return "".join( chr(x) for x in record[1])

# open the old row file, if present
old_row_file = None
old_records = []
try:
    old_row_file = open('./data/oldrows.json')
    old_row_data = old_row_file.read()
    old_records = json.loads(old_row_data)
except:
    print("No old row file found.")

db = dbm.open('./data/centroids.dbm', 'r')
#open output json file
file = open('./data/georeaps.json', 'w')
values = []
with open('./data/reapitems.csv') as csvfile:
    reader = csv.DictReader(csvfile, ['parcel', 'street', 'eligible',
                                      'paymentplan', 'lastyear',
                                      'paymentwindow', 'class',
                                      'buildingvalue'])
    count = 0
    for row in reader:
        if is_eligible(row):
            try:
                nospace_parcel = row['parcel'].replace(" ", "")
                if nospace_parcel not in db:
                    print(nospace_parcel, 'not found in centroids file.')
                    continue
                latlon = db[nospace_parcel].split()
                lot = False
                if row['buildingvalue'] == '000000000000.00':
                    lot = True
                new_record = is_new(nospace_parcel, old_records)
                if new_record:
                    count = count + 1
                    # print('New record (' + str(count) + '): ' + row['parcel'])
                values.append({
                    'pid': row['parcel'],
                    'st': row['street'] + ', ' + get_city(latlon),
                    'lat': get_lat(latlon),
                    'lon': get_lon(latlon),
                    'lot': lot,
                    'new': new_record})
            except Exception as e:
                traceback.print_exc()
                print(e)
    final_data = { 'lastupdated':datetime.now().strftime("%B %d, %Y %H:%M:%S"),
                   'points': values }
    file.write(json.dumps(final_data))
    file.close()
