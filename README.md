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

- output json: `outter_key`

- dumo file: `dump`


# Example

- Sometimes you do a query and something like this comes out:

| myid | col1      | col2      | col3     | col4    | col5   | col6   |
| :--: | :--:      | :--:      | :--:     | :--:    | :--:   | :--:   |
| 111  | category1 | cat1_val1 | yes      | `Null`  | `Null` | `Null` |
| 111  | category1 | cat1_val2 | no       | `Null`  | `Null` | `Null` |
| 111  | category1 | cat1_val3 | no       | `Null`  | `Null` | `Null` |
| 111  | category1 | cat1_val4 | yes      | `Null`  | `Null` | `Null` |
| 111  | category2 | cat2_val1 | `Null`   | `Null`  | Blue   | 100.00 |
| 111  | category2 | cat2_val2 | `Null`   | `Null`  | Blue   | 200.00 |
| 111  | category2 | cat2_val3 | `Null`   | `Null`  | Blue   | 300.00 |
| 111  | category2 | cat2_val4 | `Null`   | `Null`  | Red    | 400.00 |
| 111  | category2 | cat2_val5 | `Null`   | `Null`  | Red    | 500.00 |
| 111  | category2 | cat2_val6 | `Null`   | `Null`  | Green  | 600.00 |
| 222  | category1 | cat1_val1 | yes      | `Null`  | `Null` | `Null` |
| 222  | category1 | cat1_val2 | no       | `Null`  | `Null` | `Null` |
| 222  | category1 | cat1_val3 | no       | `Null`  | `Null` | `Null` |
| 222  | category1 | cat1_val4 | yes      | `Null`  | `Null` | `Null` |
| 222  | category2 | cat2_val1 | `Null`   | `Null`  | Cyan   | 110.00 |
| 222  | category2 | cat2_val2 | `Null`   | `Null`  | Cyan   | 220.00 |
| 222  | category2 | cat2_val3 | `Null`   | `Null`  | Black  | 330.00 |
| 222  | category2 | cat2_val4 | `Null`   | `Null`  | Black  | 440.00 |
| 222  | category2 | cat2_val5 | `Null`   | `Null`  | Yellow | 550.00 |
| 222  | category2 | cat2_val6 | `Null`   | `Null`  | Yellow | 660.00 |
||

- Just configure it to:

```
{
    "loggername" : "mylogger",
    "csv_file" : ["path/to/file.csv"],
    "csv_file_delimiter" : ";",
    "csv_reader_encoding" : "utf-8",
    "elastic_hosts" : ["localhost:9200"],
    "es_index" : "my_solution",
    "es_doc_type" : "table_to_json",
    "es_id_key" : "myid",
    "id_column" : "myid",
    "outter_key" : "mytable",
    "category_column": "col1",
    "mapping" : {
        "category1": ["col2", "col3"],
        "category2": ["col2", "col5", "col6"],
        },
    "dump": "Yes"
}
```

- And the output will be something like:

```
[
    {"id": "111",
    "mytable": {
        "category1": [
                    {"col2": "cat1_val1", "col3": "yes"},
                    {"col2": "cat1_val2", "col3": "no"},
                    {"col2": "cat1_val3", "col3": "no"},
                    {"col2": "cat1_val4", "col3": "yes"}
                    ],
        "category2": [
                    {"col2": "cat2_val1", "col5": "Cyan", "col6": "110.00"},
                    {"col2": "cat2_val2", "col5": "Cyan", "col6": "220.00"},
                    {"col2": "cat2_val3", "col5": "Black", "col6": "330.00"},
                    {"col2": "cat2_val4", "col5": "Black", "col6": "440.00"},
                    {"col2": "cat2_val5", "col5": "Yellow", "col6": "550.00"},
                    {"col2": "cat2_val6", "col5": "Yellow", "col6": "660.00"}
                    ]
                }
    },
    {"id": "222",
    "mytable": {
        "category1": [
                    {"col2": "cat1_val1", "col3": "yes"},
                    {"col2": "cat1_val2", "col3": "no"},
                    {"col2": "cat1_val3", "col3": "no"},
                    {"col2": "cat1_val4", "col3": "yes"}
                    ],
        "category2": [
                    {"col2": "cat2_val1", "col5": "Blue", "col6": "100.00"},
                    {"col2": "cat2_val2", "col5": "Blue", "col6": "200.00"},
                    {"col2": "cat2_val3", "col5": "Blue", "col6": "300.00"},
                    {"col2": "cat2_val4", "col5": "Red", "col6": "400.00"},
                    {"col2": "cat2_val5", "col5": "Red", "col6": "500.00"},
                    {"col2": "cat2_val6", "col5": "Green", "col6": "600.00"}
                    ]
                }
    }    
]
```

# Disclaimer
- If all you want is the output `json` file, just coment (`'#'`) lines `121`and `126` on `src/app.py`