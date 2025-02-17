# RecordBatchReader functionality

[Table.select()](https://vastdb-sdk.readthedocs.io/en/latest/table.html#vastdb.table.Table.select) returns a [pyarrow.RecordBatchReader](https://arrow.apache.org/docs/python/generated/pyarrow.RecordBatchReader.html#pyarrow.RecordBatchReader):

```python
Table.select(
    columns: List[str] | None = None, 
    predicate: ibis.expr.types.BooleanColumn | ibis.common.deferred.Deferred = None, 
    config: QueryConfig | None = None, 
    *, 
    internal_row_id: bool = False
  ) 
  -> pyarrow.RecordBatchReader
```

Here is a deeper dive:

- The record batches are constructed by the client from Arrow buffers read from the server (containing the actual data). The server is sending the response column-by-column, and the client collects and merges them into a single RecordBatch (by adjusting the metadata, without copying the actual data).

- RecordBatch creation isn't deterministic, since in general the data is being read in parallel, using multiple splits (each possible using a separate HTTP connection) & subsplits (each running on an internal CNode fiber).

- The RecordBatches are pushed into a [client-side size-limited queue](https://github.com/vast-data/vastdb_sdk/blob/ad4c6ae96b71d3ba3abdc3932a8a51e7c01e1f20/vastdb/table.py#L345) and then [yielded to the caller](https://github.com/vast-data/vastdb_sdk/blob/ad4c6ae96b71d3ba3abdc3932a8a51e7c01e1f20/vastdb/table.py#L405) - allowing the client (working with a RecordBatchReader) to iterate over the response in chunks, holding only a few RecordBatches in memory.

- DuckDB has a special support for RecordBatchReader objects in [its SQL syntax](https://duckdb.org/docs/guides/python/sql_on_arrow.html#apache-arrow-recordbatchreaders), by dynamically accessing the Python namespace and resolving the RecordBatchReader as a table.  E.g.

```python
from ibis import _

import duckdb
conn = duckdb.connect()

with session.transaction() as tx:
    table = tx.bucket("bucket-name").schema("schema-name").table("table-name")
    batches = table.select(columns=['c1'], predicate=(_.c2 > 2))

    # batches is a RecordBatchReader
    print(conn.execute("SELECT sum(c1) FROM batches").arrow())
```
