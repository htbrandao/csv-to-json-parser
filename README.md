# CSV to JSON
Parses data from CSV file into JSON format

Install dependencies
```
$ pip3 install -r requirements.txt

```

Run it
```
$ ./app.py --param-file=$PARAM_FILE_PATH

```

## Category and parameters

- app: `loggername`

- csv file: `csv_file`, `csv_file_delimiter`, `csv_reader_encoding`

- elasticsearch: `elastic_hosts`, `es_index`, `es_doc_type`, `es_id_key`

- columns: `field_map`, `id_column`

- output json: `outter_key`

