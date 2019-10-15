# CSV to JSON
Parses data from CSV file into JSON format

Install dependencies
```
$ pip3 install -r requirements.txt
```

Run it
```
$ ./app.py
```

## Config file (`config.json`)

- app: `loggername`

- csv file: `csv_file`, `csv_file_delimiter`, `csv_reader_encoding`

- elasticsearch: `elastic_hosts`, `es_index`, `es_doc_type`, `es_id_key`

- columns: `field_map`, `id_column`

<!-- - output json: `outter_key` -->

- dumo file: `dump`


# Example

- Sometimes you do a query and something like this comes out:

| item_id | category  | item            | available       | size             | color_available | cost            |
| :--:    | :--:   | :--:            | :--:            | :--:             | :--:            | :--:            |
| 33377   | song   | guitar          | yes             | `not important`  | `not important` | `not important` |
| 33377   | song   | electric guitar | no              | `not important`  | `not important` | `not important` |
| 33377   | song   | violin          | no              | `not important`  | `not important` | `not important` |
| 33377   | song   | piano           | yes             | `not important`  | `not important` | `not important` |
| 33377   | paint  | light           | `not important` | small            | Blue            | 100.00          |
| 33377   | paint  | dark            | `not important` | small            | Blue            | 200.00          |
| 33377   | paint  | car             | `not important` | large            | Blue            | 300.00          |
| 33377   | paint  | song            | `not important` | medium           | Red             | 400.00          |
| 33377   | paint  | indoor          | `not important` | large            | Red             | 500.00          |
| 33377   | paint  | bicycle         | `not important` | medium           | Green           | 600.00          |
| 55112   | song   | guitar          | yes             | `not important`  | `not important` | `not important` |
| 55112   | song   | electric guitar | no              | `not important`  | `not important` | `not important` |
| 55112   | song   | violin          | no              | `not important`  | `not important` | `not important` |
| 55112   | song   | piano           | yes             | `not important`  | `not important` | `not important` |
| 55112   | paint  | light           | `not important` | small            | Cyan            | 110.00          |
| 55112   | paint  | dark            | `not important` | small            | Cyan            | 220.00          |
| 55112   | paint  | car             | `not important` | large            | Black           | 330.00          |
| 55112   | paint  | song            | `not important` | medium           | Black           | 440.00          |
| 55112   | paint  | indoor          | `not important` | large            | Yellow          | 550.00          |
| 55112   | paint  | bicycle         | `not important` | medium           | Yellow          | 660.00          |


- Just configure (`config.json`) it to:

<!-- ```
{"loggername" : "mylogger",
"csv_file" : ["path/to/file01.csv", "path/to/file02.csv"],
"csv_file_delimiter" : ";",
"csv_reader_encoding" : "utf-8",
"elastic_hosts" : ["localhost:9200"],
"es_index" : "my_solution",
"es_doc_type" : "table_to_json",
"es_id_key" : "item_id",
"id_column" : "item_id",
"outter_key" : "mytable",
"category_column": "category",
"mapping" : {
    "song": ["item", "available"],
    "paint": ["item", "color_available", "cost"]
    },
"dump": "Yes"}
``` -->
```
{"loggername" : "mylogger",
"csv_file" : ["path/to/file01.csv", "path/to/file02.csv"],
"csv_file_delimiter" : ";",
"csv_reader_encoding" : "utf-8",
"elastic_hosts" : ["localhost:9200"],
"es_index" : "my_solution",
"es_doc_type" : "table_to_json",
"es_id_key" : "item_id",
"id_column" : "item_id",
"category_column": "catgr",
"mapping" : {
    "song": ["item", "available"],
    "paint": ["item", "color_available", "cost"]
    },
"dump": "Yes"}
```


- And the output will be something like:

```
[
    {
    "id": "33377 ",
    "song": [
                {"item": "guitar", "available": "yes"},
                {"item": "electric guitar", "available": "no"},
                {"item": "violin", "available": "no"},
                {"item": "piano", "available": "yes"}
            ],
    "paint": [
                {"item": "light", "size": "small", "color_available": "Cyan", "cost": "110.00"},
                {"item": "dark", "size": "small", "color_available": "Cyan", "cost": "220.00"},
                {"item": "car", "size": "large", "color_available": "Black", "cost": "330.00"},
                {"item": "song", "size": "medium", "color_available": "Black", "cost": "440.00"},
                {"item": "indoor", "size": "large", "color_available": "Yellow", "cost": "550.00"},
                {"item": "bicycle", "size": "medium", "color_available": "Yellow", "cost": "660.00"}
            ]
    },
    {
    "id": "55112 ",
    "song": [
                {"item": "guitar", "available": "yes"},
                {"item": "electric guitar", "available": "no"},
                {"item": "violin", "available": "no"},
                {"item": "piano", "available": "yes"}
            ],
    "paint": [
                {"item": "light", "size": "small", "color_available": "Cyan", "cost": "110.00"},
                {"item": "dark", "size": "small", "color_available": "Cyan", "cost": "220.00"},
                {"item": "car", "size": "large", "color_available": "Black", "cost": "330.00"},
                {"item": "song", "size": "medium", "color_available": "Black", "cost": "440.00"},
                {"item": "indoor", "size": "large", "color_available": "Yellow", "cost": "550.00"},
                {"item": "bicycle", "size": "medium", "color_available": "Yellow", "cost": "660.00"}
            ]
    }
]
```

# Disclaimer

- App logs and appends to `/tmp/$LOGGER_NAME.log`
- App dumps `.json` output files to `/tmp/csv-to-json-dump_$TIMESTAMP.json`

- Bring ELK up

    `$ docker run -p 9200:9200 -p 9300:9300 --name elastic -e "discovery.type=single-node" -d docker.elastic.co/elasticsearch/elasticsearch:7.3.2`

    `$ docker run --link elastic:elasticsearch --name kibana -p 5601:5601 -d docker.elastic.co/kibana/kibana:7.3.2`

- If all you want is the output `json` file, just coment (`'#'`) the following lines in `src/app.py`:

    `# es = Elasticsearch(hosts=elastic_hosts)`

    `# bulk = elastic_bulk_index(index=es_index, docType=es_doc_type, data=obj, _id_key=es_id_key, elastic=es)`

    `# sr = sentRate(total=len(obj), good=bulk)`