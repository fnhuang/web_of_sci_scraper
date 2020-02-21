from pathlib import Path
from os import mkdir, path, remove
import csv
from utilities import is_locked, file_lock_wait_sc
import time



def write_doc_info(city_year, identifier, iden_type, journal_name, num_citation, doc_type,
                   published_day, published_month, published_year,
                   ra, wora, auth_sequence, reprint_authors, is_highly_cited, is_hot_paper):
    year_dir = str(city_year.year)
    city_dir = str(city_year.year) + "/" + str(city_year.name)
    year_file = str(city_year.year) + "/" + city_year.name + "/" + \
                str(city_year.start_doc) + "_doc_info.csv"

    auth_sequence_text = " and ".join(auth_sequence)
    reprint_authors_text = " and ".join(reprint_authors)

    if not path.isdir(year_dir):
        mkdir(year_dir)

    if not path.isdir(city_dir):
        mkdir(city_dir)

    if not path.isfile(year_file):
        header = [['doc', 'identifier', 'iden_type', 'journal_name', 'num_citation', 'doc_type',
                   'published_day','published_month','published_year',
                   'research_area', 'wos_research_area', 'authors_in_seq', 'reprint_authors',
                   'highly_cited', 'hot_paper']]
        my_file = open(year_file, "w", newline="")
        writer = csv.writer(my_file)
        writer.writerows(header)
        my_file.close()

    while is_locked(year_file):
        print("%s is currently in use, waiting %s seconds" %
              (year_file, file_lock_wait_sc))
        time.sleep(file_lock_wait_sc)

    my_file = open(year_file, "a", newline='')
    writer = csv.writer(my_file)

    writer.writerows([[city_year.doc_crawled, identifier, iden_type, journal_name, num_citation, doc_type,
                       published_day, published_month, published_year,
                       ra, wora, auth_sequence_text, reprint_authors_text, is_highly_cited,
                       is_hot_paper]])
    my_file.close()

def write_addresses(city_year, addresses):
    year_dir = str(city_year.year)
    city_dir = str(city_year.year) + "/" + str(city_year.name)
    year_file = str(city_year.year) + "/" + city_year.name + "/" + \
                str(city_year.start_doc) + "_authors_addresses.csv"


    if not path.isdir(year_dir):
        mkdir(year_dir)
    if not path.isdir(city_dir):
        mkdir(city_dir)


    if not path.isfile(year_file):
        header = [['doc', 'authors', 'address', 'org']]
        my_file = open(year_file, "w", newline="")
        writer = csv.writer(my_file)
        writer.writerows(header)
        my_file.close()


    for address in addresses:
        address.insert(0, city_year.doc_crawled)


    while is_locked(year_file):
        print("%s is currently in use, waiting %s seconds" %
              (year_file, file_lock_wait_sc))
        time.sleep(file_lock_wait_sc)


    my_file = open(year_file, "a", newline='')
    writer = csv.writer(my_file)
    writer.writerows(addresses)
    my_file.close()
