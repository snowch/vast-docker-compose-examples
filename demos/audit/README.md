# Audit Log Notes (WIP)

- see [policy, e.g. docs URL TBC](https://support.vastdata.com/s/article/UUID-30463b32-c72f-ecaf-2864-15c12ffa5182)
- Use superset:
  - vast-audit-log-bucket|vast_audit_log_schema
  - change parameters (TBC)
```sql
SELECT *
FROM "vast-big-catalog-bucket|vast_big_catalog_schema".vast_big_catalog_table
WHERE parent_path like '/csnow%'
LIMIT 100
```

