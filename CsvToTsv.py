# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 19:49:11 2018

@author: andi3
"""

import csv

with open(r'C:\Users\andi3\OneDrive\Documents\utilities\csvToTsv\level1.csv','r') as csvin, open(r'C:\Users\andi3\OneDrive\Documents\utilities\csvToTsv\leve11.tsv', 'w') as tsvout:
    csvin = csv.reader(csvin)
    tsvout = csv.writer(tsvout, delimiter='\t')

    for row in csvin:
        tsvout.writerow(row)