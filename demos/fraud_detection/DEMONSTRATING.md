# Demonstrating the Fraud Detection demo

> [!NOTE]
> The demo environment is running small docker instances.  Don't expect snappy response times.

## Endpoints

From the root project repo, run:

```bash
./scripts/endpoints_all.sh
```

Make a note of your project endpoints.

## Setup

> [!NOTE]
> verytime you run the project, start by executing the 

Open the Jupyter-Spark url (see [endpoints](#endpoints), above).

- Navigate to the **examples/fraud_detection/** folder
- Open the **Setup_environment.ipynb** notebook
- Run all the cells in the notebook

## Running

## Kafka Producer

This process writes simulated data to Kafka.

- Navigate to the **examples/fraud_detection/** folder
- Open the **Fraud_detect_producer.ipynb** notebook
- In the menu, select **Kernel** > **Restart Kernel and Run All Cells...**
- Note that after a few seconds, you should see the output.  The number of records should be continuously increasing.

```
Produced: 88839 records
```

## Kafka Consumer

This process reads records from Kafka and writes to the Vast DB.

- Navigate to the **examples/fraud_detection/** folder
- Open the **Consume_IdentifyFraud.ipynb** notebook
- In the menu, select **Kernel** > **Restart Kernel and Run All Cells...**
- Note that after a few seconds, you should see the output.  The number of records should be continuously increasing.

```
Starting Spark streaming job...
Last update: 08:50:30 | Batch 0: 0 records | Total messages: 0 | DB rows: 0   
```

## Superset

Open the Dashboard "Trading".  See the demo video for inspiration!

![Demo](https://media.githubusercontent.com/media/snowch/vast-docker-compose-examples/refs/heads/main/demos/fraud_detection/assets/VAST-Trading-Fraud-Demo2.gif)


## Shutdown

Click the stop button on both the **Fraud_detect_producer.ipynb** notebook and the **Consume_IdentifyFraud.ipynb** notebook.
