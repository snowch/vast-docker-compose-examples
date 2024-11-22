# Audit Log Notes (WIP)

- ensure your username is set in **VMS -> Settings -> Auditing -> Read-access Users**
- Use superset:
  - vast-audit-log-bucket|vast_audit_log_schema

```sql
SELECT *
FROM "vast-audit-log-bucket|vast_audit_log_schema".vast_audit_log_table
LIMIT 100
```


