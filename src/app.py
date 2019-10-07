#!/usr/bin/env python3

import os
import csv
import json
import logging
import pandas as pd
from time import time
from datetime import datetime
from elasticsearch import Elasticsearch, ElasticsearchException, helpers

# ==================================================================== #
# functions
# ==================================================================== #

def logger(name: str):
    log_format = '%(levelname)s %(asctime)s %(name)s %(message)s'
    logging.basicConfig(filename='/tmp/csv-to-json.log', filemode='a', format=log_format)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def load_csv(filepath: str, delimiter: str, header='infer', encoding='utf-8'):
    logger.info('Loading {}'.format(filepath))
    return pd.read_csv(filepath, delimiter=delimiter, header=header, encoding=encoding, dtype=object)

def find_ids(df, id_column: str):
    return list(set(df[id_column]))

def id_count(df, id_column: str):
    return len(list(set(df[id_column])))

def single_id_df(df, id_column: str, id_value: any):
    return df[df[id_column] == id_value]

def extract_features_by_category(single_id_df, category: str, related_features: list, category_column: str):
    lc = [ [str(reg[i]).rstrip().lower() for i in range(len(reg)) ] 
          for reg in single_id_df[single_id_df[category_column] == category][related_features].values ]
    related_features = [feat.lower() for feat in related_features]
    out = []
    for reg in lc:
        out.append(dict(zip(related_features, reg)))
    category_key = category.lower()
    category_dict = {category_key: out}
    return category_dict

def curriculum_json_generator(df, field_map: dict, id_column: str, outter_key: str, category_column: str):
    id_list = find_ids(df=df, id_column=id_column)
    logger.info('Found {} units on \'{}\' to process'.format(len(id_list), id_column))
    out = []
    for f_id in id_list:
        f_info = {'matricula': str(f_id), '@timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), outter_key: {} }
        f_df = single_id_df(df=df, id_column=id_column, id_value=f_id)
        for key in field_map.keys():
            try:
                f_info[outter_key][key.lower()] = extract_features_by_category(single_id_df=f_df,
                                                                                category=key,
                                                                                category_column=category_column,
                                                                                related_features=field_map[key])[key.lower()]
            except:
                logger.error('id: {} key: \'{}\''.format(f_id, key))
        out.append(f_info)
    logger.info('Generated: {}. Delta: {}'.format(len(out), len(out)-len(id_list)))
    return out

def elastic_bulk_index (index: str, docType: str, data: list, elastic, _id_key: str):
    bulk = [{"_index": index, "_type": docType, "_id": reg[_id_key], "_source": reg} for reg in data]
    return helpers.bulk(client=elastic, actions=bulk)[0]

def sentRate(total: int, good: int):
    acc = 100.0 - ((total - good)/total)
    logger.info('Delivery rate {}%'.format(acc))
    return acc

def dump_json(obj: dict, yes_or_no: str):
    if yes_or_no.lower() == "yes":
        file_name = 'dump_{}.json'.format(datetime.now()).replace(" ", "_")
        with open('dump/{}'.format(file_name), 'w') as json_file:
            json.dump(obj, json_file)
            logger.info('Generated {}'.format(file_name))
    return yes_or_no
        
# ==================================================================== #
# config variables
# ==================================================================== #

with open('config.json') as config_file:
    config = json.load(config_file)

loggername = config['loggername']
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
outter_key = config['outter_key']
dump = config['dump']

# ==================================================================== #
# main
# ==================================================================== #

if __name__ == '__main__':

    logger = logger(loggername)
    logger.info('START PARSING')
    ts1 = time()
    es = Elasticsearch(hosts=elastic_hosts)
    for csv_file in csv_files:
        df = load_csv(filepath=csv_file, delimiter=csv_file_delimiter, header='infer', encoding=csv_reader_encoding)
        obj = curriculum_json_generator(df=df, field_map=mapping, id_column=id_column, outter_key=outter_key, category_column=category_column)
        bulk = elastic_bulk_index(index=es_index, docType=es_doc_type, data=obj, _id_key=es_id_key, elastic=es)
        sr = sentRate(total=len(obj), good=bulk)
        dump_json(obj=obj, yes_or_no=dump)
    logger.info('Runtime: {0:.2f} seconds'.format(time()-ts1))
    logger.info('END PARSING')
