import csv

def extract_bijection_csv(path_to_file):
    bijection = []
    with open(path_to_file) as datafile:
        reader = csv.reader(datafile)
        for line in reader:
            if not any(len(_) > 8 for _ in line):
                yield line[:2]

