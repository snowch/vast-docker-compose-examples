# Audit Log Notes (WIP)

- Ensure your username is set in **VMS -> Settings -> Auditing -> Read-access Users**
- Use Superset + Trino with the Vast DB connection:
  - vast-audit-log-bucket|vast_audit_log_schema

```sql
SELECT *
FROM "vast-audit-log-bucket|vast_audit_log_schema".vast_audit_log_table
LIMIT 100
```
- Use Jupyter + Trino:
  - See the notebook example available in the jupyter-pyspark image: `/examples/sql_notebooks/auditlog.ipynb`
  - You can also view the notebook on github [here](https://github.com/snowch/vast-docker-compose-examples/blob/main/jupyter-pyspark/examples/sql_notebooks/auditlog.ipynb)


