#!/usr/bin/env python3

import json
import os
import logging
from time import sleep, time
import pandas as pd
import csv
from elasticsearch import Elasticsearch, ElasticsearchException, helpers

# ==================================================================== #
# functions
# ==================================================================== #

def logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s %(asctime)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def load_csv(filepath: str, delimiter: str, header='infer', encoding='utf-8'):
    return pd.read_csv(filepath, delimiter=delimiter, header=header, encoding=encoding)   

def find_ids(df, id_column: str):
    return list(set(df[id_column]))

def id_count(df, id_column: str):
    return len(list(set(df[id_column])))

def single_id_df(df, id_column: str, id_value: any):
    return df[df[id_column] == id_value]

def extract_features_by_category(single_id_df, category: str, related_features: list):
    lc = [ [str(reg[i]).rstrip().lower() for i in range(len(reg)) ] 
          for reg in single_id_df[single_id_df['TIPO'] == category][related_features].values ]
    related_features = [feat.lower() for feat in related_features]
    out = []
    for reg in lc:
        out.append(dict(zip(related_features, reg)))
    category_key = category.lower()
    category_dict = {category_key: out}
    return category_dict

def curriculum_json_generator(df, field_map: dict, id_column: str, outter_key: str):
    id_list = find_ids(df=df, id_column=id_column)
    logger.info('Found \'{}\' units on \'{}\' to process'.format(len(id_list), id_column))
    out = []
    for f_id in id_list:
        f_info = {'matricula': str(f_id), outter_key: {} }
        f_df = single_id_df(df=df, id_column=id_column, id_value=f_id)
        for key in field_map.keys():
            try:
                f_info[outter_key][key.lower()] = extract_features_by_category(single_id_df=f_df, category=key, related_features=field_map[key])[key.lower()]
            except:
                logger.error('id: \'{}\' key: \'{}\''.format(f_id, key))
        out.append(f_info)
    logger.info('Generated: \'{}\'. Delta: \'{}\''.format(len(out), len(out)-len(id_list)))
    return out

def elastic_bulk_index (index: str, docType: str, data: list, elastic, _id_key: str):
    bulk = []
    for reg in data:
        k = reg[_id_key]
        bulk.append({"_index": index, "_type": docType, "_id": k, "_source": reg})
    return helpers.bulk(client=elastic, actions=bulk)[0]

def sentRate(total: int, good: int):
    acc = 100.0 - ( (total - good)/total)
    logger.info('Delivery rate {}%'.format(acc))
    return acc

# ==================================================================== #
# global variables
# ==================================================================== #

loggername = 'people_analytics'

csv_file = '/home/f4119597/Downloads/peopleAnalytics/ListaGeralDitec-VRS20191001/QueryDB2TAO-GERAL-DITEC-VRS20191001.csv'
csv_file_delimiter = ';'
csv_reader_encoding = 'cp1252'

elastic_hosts = ['localhost:9200']
es_index = 'people_analytics'
es_doc_type = 'curriculo'
es_id_key = 'matricula'

mapping = {
    'CAPACIDADE': ['NOME', 'ATIVO', 'CODIGO'],
    'CONHECIMENTO': ['NOME', 'CODIGO', 'NIVEL', 'CODIGO_AREA', 'CODIGO_SUB_AREA'],
    'FERRAMENTA': ['NOME', 'CODIGO', 'ATIVO'],
    'INTERESSE': ['NOME', 'CODIGO'],
    'MOTIVACAO': ['NOME', 'CODIGO'],
    'REALIZACAO': ['NOME', 'CODIGO'],
    'FORMACAO_SUPERIOR': ['NOME',
    'CODIGO', 'NIVEL', 'DATA_FIM', 'MODALIDADE', 'NATUREZA', 'URL', 'ESTADO', 'NOME_INSTITUICAO_ENSINO']
    }

id_column = 'MATRICULA_FUNCIONARIO'
outter_key = 'curriculo'

# ==================================================================== #
# main
# ==================================================================== #

if __name__ == '__main__':

    logger = logger(loggername)
    logger.info('START PROCESS')
    ts1 = time()
    es = Elasticsearch(hosts=elastic_hosts)
    df = load_csv(filepath=csv_file, delimiter=csv_file_delimiter, header='infer', encoding=csv_reader_encoding)
    obj = curriculum_json_generator(df=df, field_map=mapping, id_column=id_column, outter_key=outter_key)
    bulk = elastic_bulk_index(index=es_index, docType=es_doc_type, data=obj, _id_key=es_id_key, elastic=es)
    sr = sentRate(total=len(obj), good=bulk)
    logger.info('Runtime: {} seconds'.format(time()-ts1))
    logger.info('END PROCESS')
    