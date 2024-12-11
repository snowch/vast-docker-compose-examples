# Catalog Demo

- Setup your policy, e.g. VMS https://support.vastdata.com/s/article/Client-Access-to-the-VAST-Catalog-873214
- Use Superset + Trino with the Vast DB connection:
  - vast-big-catalog-bucket|vast_big_catalog_schema
  - change parameters:
    
```sql
SELECT *
FROM "vast-big-catalog-bucket|vast_big_catalog_schema".vast_big_catalog_table
WHERE parent_path like '/csnow%'
LIMIT 100
```
- Use Jupyter + Trino:
  - See the notebook example available in the jupyter-pyspark image: `/examples/sql_notebooks/catalog.ipynb`
  - You can also view the notebook on github [here](https://github.com/snowch/vast-docker-compose-examples/blob/main/jupyter-pyspark/examples/sql_notebooks/catalog.ipynb)
