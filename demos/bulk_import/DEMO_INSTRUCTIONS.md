# Demonstrating Bulk Loading

> [!NOTE]
> The demo environment is running small docker instances.  Don't expect snappy response times.

## Endpoints

From the root project repo, run:

```bash
./scripts/endpoints_all.sh
```

Make a note of your project endpoints.

## Start Tweet Simulator

In this section we start producing tweets that are sent to Kafka.

Open the NiFi url (see [endpoints](#endpoints), above).

- Right Click on the Canvas background and click **Enable All Controller Services**
- Double Click on **Demo_Flow** to open it
- Double Click on **Bulk Import** to open it
- Double Click on **ListS3** to open it
  - Note the **Bucket**, **Endpoint Override URL** and **Prefix** properties
  - The **ListS3** processeor polls this location and send the list of new files it finds to the **ImportVastDB** processor
  - Start the **ListS3** processor

 - Right Click on the **ImportVastDB** processor
   - Note the Database Bucket, Schema and Table name
   - Imported Parquet files will get saved to this table
   - The table will get created if it doesn't exist beforehand.
  
## Add a Parquet file

- Open the Jupyter_Spark notebook (Open the Jupyter_Spark url (see [endpoints](#endpoints), above).
- Run the **BulkImport.ipynb** in the **examples** folder (coming soon)
- This notebook
   - Downloads the [userdata/](./assets/userdata/) files
   - Uses s3cmd to upload each file to the s3 bucket being monitored by the NiFi **ListS3** processor
 
## View Imported Data in Superset

In  this section, we query the tweets in real-time using Apache Superset.

Open the Superset url (see [endpoints](#endpoints), above).

- In the Superset toolbar, click on **SQL** >> **SQL Lab**
- On left side of page, set the following options:
  - **Database**: Trino VastDB
  - **Schema**: Your Bulk Import Schema
  - **Table**: Your Bulk Import Table
- Run the following query a few times (replace `csnowdb|social_media".users` with your details):

```sql
SELECT
*
FROM "csnowdb|social_media".users
ORDER BY created_at DESC
LIMIT 5
```
