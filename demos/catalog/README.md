# Catalog Notes (WIP)

- see policy, e.g. VMS https://support.vastdata.com/s/article/Client-Access-to-the-VAST-Catalog-873214
- Use superset:
  - vast-big-catalog-bucket|vast_big_catalog_schema
  - change parameters:
    
```sql
SELECT *
FROM "vast-big-catalog-bucket|vast_big_catalog_schema".vast_big_catalog_table
WHERE parent_path like '/csnow%'
LIMIT 100
```

