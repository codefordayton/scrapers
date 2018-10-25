#!env/bin/python
""" Splits a reapitems.csv into city and county properties """
import csv
import re

def split_reap_items():
    """ Splits the reapitems.csv into into city and county properties

    Args:
        None - Assumes reapitems is in the same directory

    Returns:
        None"""
    h_in = open("./reapitems.csv", "r")
    h_city = open("./cityreapitems.csv", "w")
    h_county = open("./countyreapitems.csv", "w")

    patternobj = re.compile('^R72.*$')

    reader = csv.reader(h_in)
    citywriterobj = csv.writer(h_city)
    countywriterobj = csv.writer(h_county)

    for line in reader:
        if patternobj.match(line[0]) != None:
            citywriterobj.writerow(line)
        else:
            countywriterobj.writerow(line)

    h_in.close()
    h_city.close()
    h_county.close()

if __name__ == "__main__":
    split_reap_items()
