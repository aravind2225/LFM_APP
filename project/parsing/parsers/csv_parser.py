"""
This is a csv parser
"""

import csv

def parse_csv(file_obj):
    """
    Docstring for parse_csv
    we will convert the csv file into a dictionary
    
    :param file_obj: input file
    """
    reader = csv.DictReader(
        file_obj.read().decode("utf-8").splitlines()
    )
    for row in reader:
        yield row
