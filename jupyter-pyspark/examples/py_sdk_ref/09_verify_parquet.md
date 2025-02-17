# Utility: Verify Parquet

Checks if a parquet file can be loaded into Vast DB.

Vast DB is able to import Parquet files from Vast S3 in a highly optimised manner.  The Python SDK methods are:

- [vastdb.Table.import_files](https://vastdb-sdk.readthedocs.io/en/latest/table.html#vastdb.table.Table.import_files)
- [vastdb.table.Table.import_partitioned_files](https://vastdb-sdk.readthedocs.io/en/latest/table.html#vastdb.table.Table.import_partitioned_files)
- [vastdb.util.create_table_from_files](https://vastdb-sdk.readthedocs.io/en/latest/util.html#vastdb.util.create_table_from_files)

The vastdb import functionality requires parquet files to have only [supported datatypes](https://github.com/vast-data/vastdb_sdk/blob/main/docs/types.md).  This page provides an example script to verify columns in a parquet file and print out any offending columns.


## Limitations

- Currently unable to calculate max column size for nested types (List, Map, Struct).

## Install

```bash
pip3 install --upgrade --quiet git+https://github.com/snowch/vastdb_parq_schema_file.git --use-pep517
```

## Examples

### New York Taxi Data

![NYT Data](img/taxi_data.gif)

### Column too wide example:

![String field too large](img/string_field_too_large.gif)
