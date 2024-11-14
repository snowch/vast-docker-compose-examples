# Demonstrating Bulk Loading

In this section we demonstrate bulk loading parquet files into Vast DB from Vast S3.  We use NiFi, but bulk loading can be performed using the VastDB Python SDK, Trino, and Spark.  Under the hood, the NiFi Bulk Load (ImportVastDB) processor uses the VastDB Python SDK.

> [!NOTE]
> The demo environment is running small docker instances.  Don't expect snappy response times.

## Endpoints

From the root project repo, run:

```bash
./scripts/endpoints_all.sh
```

Make a note of your project endpoints.

## Start Bulk Load processors

In this section we start the bulk loader Nifi processors

- Open the NiFi url (see [endpoints](#endpoints), above).
- Right Click on the Canvas background and click **Enable All Controller Services**
- Double Click on **Demo_Flow** to open it
- Double Click on **Bulk Import** to open it
- Double Click on **ListS3** to open it
  - Note the **Bucket**, **Endpoint Override URL** and **Prefix** properties
  - The **ListS3** processeor polls this location and send the list of new files it finds to the **ImportVastDB** processor
  - Start the **ListS3** processor

 - Double Click on the **ImportVastDB** processor
   - Note the Database properties such as Endpoint, Bucket, Schema and Table name
   - Parquet files will get bulk loaded to this table
   - The table will get created if it doesn't exist beforehand
  
> [!TIP]
> If your files aren't getting imported, check the state of the **ListS3** processor by right clicking and **View State**.
> Reset state if required by first stopping the processor.
  
## Add a Parquet file to S3

- Open the **Jupyter-Spark** url (see [endpoints](#endpoints), above)
- Run the **NiFi_Bulk_Load.ipynb** in the **examples** folder.  The notebook:
   - Downloads the [userdata/](./assets/userdata/) files (userdata1.parquet ... userdata5.parquet)
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
