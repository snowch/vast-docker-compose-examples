DROP TABLE IF EXISTS hive.catalog_output.catalog_table;
DROP SCHEMA IF EXISTS hive.catalog_output;
CREATE SCHEMA IF NOT EXISTS hive.catalog_output
WITH (
  location = 's3a://csnow-bucket/hive_catalog_output'
);

CREATE TABLE hive.catalog_output.catalog_table
WITH (
  format = 'CSV',
  csv_separator = ',',
  csv_quote = '"',
  csv_escape = '\'
)
AS (
  SELECT
        CAST(phandle.clone_id AS varchar) AS phandle_clone_id,
        CAST(phandle.handle_id AS varchar) AS phandle_handle_id,
        CAST(creation_time AS varchar) AS creation_time,
        CAST(uid AS varchar) AS uid,
        CAST(owner_sid AS varchar) AS owner_sid,
        CAST(owner_name AS varchar) AS owner_name,
        CAST(gid AS varchar) AS gid,
        CAST(group_owner_sid AS varchar) AS group_owner_sid,
        CAST(group_owner_name AS varchar) AS group_owner_name,
        CAST(atime AS varchar) AS atime,
        CAST(mtime AS varchar) AS mtime,
        CAST(ctime AS varchar) AS ctime,
        CAST(nlinks AS varchar) AS nlinks,
        CAST(element_type AS varchar) AS element_type,
        CAST(size AS varchar) AS size,
        CAST(used AS varchar) AS used,
        CAST(tenant_id AS varchar) AS tenant_id,
        name,
        extension,
        parent_path,
        symlink_path,
        CAST(major_device AS varchar) AS major_device,
        CAST(minor_device AS varchar) AS minor_device,
        CAST(s3_locks_retention.mode AS varchar) AS s3_locks_retention_mode,
        CAST(s3_locks_retention.timeout AS varchar) AS s3_locks_retention_timeout,
        CAST(nfs_mode_bits AS varchar) AS nfs_mode_bits,
        CAST(name_aces_exist AS varchar) AS name_aces_exist,
        CAST(s3_locks_legal_hold AS varchar) AS s3_locks_legal_hold,
        CAST(user_tags_count AS varchar) AS user_tags_count,
        CAST(json_format(CAST(user_metadata AS json)) AS varchar) AS user_metadata,
        CAST(json_format(CAST(user_tags AS json)) AS varchar) AS user_tags,
        login_name,
        search_path
  FROM vast."vast-big-catalog-bucket|vast_big_catalog_schema".vast_big_catalog_table
  LIMIT 100
);

SELECT * FROM hive.catalog_output.catalog_table;
