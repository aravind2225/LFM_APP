import csv

def parse_csv(file_obj):
    reader = csv.DictReader(
        file_obj.read().decode("utf-8").splitlines()
    )
    for row in reader:
        yield row
