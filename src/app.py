#!/usr/bin/env python3

import os
import csv
import json
import logging
import unicodedata
import pandas as pd
from time import time
from datetime import datetime
from elasticsearch import Elasticsearch, ElasticsearchException, helpers

# ==================================================================== #
# functions
# ==================================================================== #

def create_logger(name: str):
    """
    Sets up a logger, both on the terminal stdout and on the file system under the /tmp folder.
    """
    log_format = '%(levelname)s %(asctime)s %(name)s %(message)s'
    logging.basicConfig(filename='/tmp/{}.log'.format(name), filemode='a', format=log_format)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger #logger

def load_csv(filepath: str, delimiter: str, header='infer', encoding='utf-8'):
    """
    Loads .csv file and returns a pandas.DataFrame object.
    """
    logger.info('Loading {}'.format(filepath))
    return pd.read_csv(filepath, delimiter=delimiter, header=header, encoding=encoding, dtype=object) #pandas.DataFrame

def find_ids(df, id_column: str):
    """
    Reads a dataframe and returns a list of unique data from the id_column.
    """
    return list(set(df[id_column])) #list

def id_count(df, id_column: str):
    """
    Count the amount of ids from the data frame for future accountability.

    Returns an int.
    """
    return len(list(set(df[id_column]))) #list

def single_id_df(df, id_column: str, id_value: any):
    """
    Creates a pandas.DataFrame for a single id value, somewhat like a SQL Subselect.

    Returns a panda.DataFrame.
    """
    return df[df[id_column] == id_value] #pandas.DataFrame

def remove_accents(input_str):
    """
    Removes common alphabetic accentuation from strings.
    """
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)]) #string

def extract_features_by_category(single_id_df, category: str, related_features: list, category_column: str):
    """
    Parses the 'single id dataframe' for the desired category and it's related features (columns).
    """
    lc = [[remove_accents(str(reg[i]).rstrip().lower()) for i in range(len(reg)) ] 
          for reg in single_id_df[single_id_df[category_column] == category][related_features].values ]
    related_features = [feat.lower() for feat in related_features]
    out = []
    for reg in lc:
        out.append(dict(zip(related_features, reg)))
    category_key = category.lower()
    category_dict = {category_key: out}
    return category_dict #dict

def csv_to_json_generator(df, field_map: dict, id_column: str, category_column: str):
    """
    Creates a dictionary/json structure for a `single id dataframe` extracting content using the
    `extract_features_by_category` function.
    """
    id_list = find_ids(df=df, id_column=id_column)
    logger.info('Found {} units on \'{}\' to process'.format(len(id_list), id_column))
    out = []
    for f_id in id_list:
        f_info = {'id': str(f_id), '@timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}
        f_df = single_id_df(df=df, id_column=id_column, id_value=f_id)
        for key in field_map.keys():
            try:
                data = extract_features_by_category(single_id_df=f_df, category=key, category_column=category_column,
                                                    related_features=field_map[key])[key.lower()]
                f_info[key.lower()] = data
            except:
                logger.error('id: {} key: \'{}\''.format(f_id, key))
        out.append(f_info)
    logger.info('Generated: {}. Delta: {}'.format(len(out), len(out)-len(id_list)))
    return out #list(dict)

def elastic_bulk_index (index: str, docType: str, data: list, elastic, _id_key: str):
    """
    Sends collection of data to the desired Elasticsearch cluster/node.
    """
    bulk = [{"_index": index, "_type": docType, "_id": reg[_id_key], "_source": reg} for reg in data]
    return helpers.bulk(client=elastic, actions=bulk)[0] #int

def sent_rate(total: int, good: int):
    """
    Gives a percentage metric for sent data vs all data.
    """
    acc = 100.0 - ((total - good)/total)
    logger.info('Delivery rate {}%'.format(acc))
    return acc #float

def dump_json(obj: dict, yes_or_no: str):
    """
    Writes a parsed .csv file to file system.
    """
    if yes_or_no.lower() == "yes":
        file_name = '/tmp/csv-to-json-dump_{}.json'.format(datetime.now()).replace(" ", "_")
        with open('{}'.format(file_name), 'w') as json_file:
            json.dump(obj, json_file)
            logger.info('Generated {}'.format(file_name))
    return yes_or_no #string

# ================================================================================================ #

def main():
    es = Elasticsearch(hosts=elastic_hosts)
    for csv_file in csv_files:
        df = load_csv(filepath=csv_file, delimiter=csv_file_delimiter, header='infer', encoding=csv_reader_encoding)
        obj = csv_to_json_generator(df=df, field_map=mapping, id_column=id_column, category_column=category_column)
        bulk = elastic_bulk_index(index=es_index, docType=es_doc_type, data=obj, _id_key=es_id_key, elastic=es)
        sent_rate(total=len(obj), good=bulk)
        dump_json(obj=obj, yes_or_no=dump_flag)


if __name__ == '__main__':

    with open('config.json') as config_file:
        config = json.load(config_file)
        logger_name = config['logger_name']
        csv_files = config['csv_file']
        csv_file_delimiter = config['csv_file_delimiter']
        csv_reader_encoding = config['csv_reader_encoding']
        elastic_hosts = config['elastic_hosts']
        es_index = config['es_index']
        es_doc_type = config['es_doc_type']
        es_id_key = config['es_id_key']
        category_column = config['category_column']
        mapping = config['mapping']
        id_column = config['id_column']
        # outter_key = config['outter_key']
        dump_flag = config['dump_flag']

    logger = create_logger(logger_name)
    logger.info('START PARSING')

    ts1 = time()

    main()

    logger.info('Runtime: {0:.2f} seconds'.format(time()-ts1))
    logger.info('END PARSING')
