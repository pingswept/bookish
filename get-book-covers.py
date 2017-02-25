#!/usr/bin/python

import csv
import requests
import os
import sys
import time

if __name__ == '__main__':

    infile = csv.reader(open(sys.argv[1], 'r'))
    infile.next() # skip header row
    for line in infile:
        print line[6]
        isbn13 = str(line[6])
        base_url = "http://covers.openlibrary.org/b/isbn/"
        filename_small = isbn13 + "-S.jpg"
        filename_large = isbn13 + "-L.jpg"

       	for name in [filename_small, filename_large]:
       		image_path = "img/" + name
       		if not os.path.isfile(image_path):
	       		time.sleep(5)
		        r = requests.get(base_url + name, stream=True)
		        if r.status_code == 200:
		            with open(image_path, 'wb') as f:
			            for chunk in r:
			                f.write(chunk)