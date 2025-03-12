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

- Navigate to the **examples/fraud_detection/** folder
- Open the **Fraud_detect_producer.ipynb** notebook
- In the menu, select **Kernel** > **Restart Kernel and Run All Cells...**
- Note that after a few seconds, you should see the output.  The number of records should be continuously increasing.

```
Produced: 88839 records
```

## Shutdown


