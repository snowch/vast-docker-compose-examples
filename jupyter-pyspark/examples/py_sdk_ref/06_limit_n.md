# Query with 'LIMIT n'

```{seealso}
The Vast DB SDK API Documentation is available [here](https://vastdb-sdk.readthedocs.io).
```

## Overview

A common operation when interactively working with large datasets is to LIMIT the records returned so can quickly view some data without processing the whole dataset.

For more information see:

- [Tuning: splits and subplits](../tuning/python/howto.md)
- [vastdb.Table.select()](https://vastdb-sdk.readthedocs.io/en/latest/table.html#vastdb.table.Table.select)
- [pyarrow.RecordBatchReader](https://arrow.apache.org/docs/python/generated/pyarrow.RecordBatchReader.html)

## Instructions

Let’s say you have a large table with 10 million rows. You want to execute a query that returns only a small set of rows, similar to the SQL LIMIT operator (e.g. `SELECT * FROM table LIMIT n`).

Here’s how you might configure it:

```python
from vastdb.config import QueryConfig

config = QueryConfig(
  num_splits=1,                	 # Manually specify 1 split
  num_sub_splits=1,              # Each split will be divided into 1 subsplits
  limit_rows_per_sub_split=10,   # Each subsplit will process 10 rows at a time
)
```

Here's how it can be used:

```python
import pyarrow
import vastdb

session = vastdb.connect(
    endpoint=ENDPOINT, access=ACCESS_KEY, secret=SECRET_KEY
)

with session.transaction() as tx:
    table = tx.bucket(DB_BUCKET).schema(DB_SCHEMA).table(DB_TABLE)

    batches = table.select(config=config)
    first_batch = next(batches)

    assert first_batch.num_rows == 10
```

Note that `table.select()` returns a `pyarrow.RecordBatchReader` and we take the first batch.  We then verify that batch has 10 rows.