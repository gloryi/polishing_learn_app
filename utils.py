'''utils to process csv files'''
import csv
from config import DATA_SIZE


def extract_bijection_csv(path_to_file):
    '''extract two cols from csv with bijectns key,feature'''
    with open(path_to_file, encoding="UTF-8") as datafile:
        reader = csv.reader(datafile)
        for line in reader:
            # if not any(len(_) > 8 for _ in line):
            yield line[:2]


def crop_data(path_to_file):
    '''rewrite data file to left N last lines only'''
    lines = []
    with open(path_to_file, "r", encoding="UTF-8") as datafile:
        reader = csv.reader(datafile)
        lines = list(reader)

    if len(lines) > DATA_SIZE:
        heads = len(lines)-DATA_SIZE
        lines = lines[heads:]

    with open(path_to_file, "w", encoding="UTF-8") as datafile:
        writer = csv.writer(datafile)
        writer.writerows(lines)
