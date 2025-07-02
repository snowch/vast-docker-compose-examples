# Introduction: Cross-Source Similarity MVP for Fraud Detection

- **Date:** Tuesday, April 22, 2025
- **Location:** Reading, England, United Kingdom

## Overview: The Challenge of Modern Fraud Detection

Detecting sophisticated financial crime and fraud is increasingly challenging. Adversaries often orchestrate schemes that leave subtle footprints across multiple, often siloed, datasets – tax filings, property records, company directorships, bank transactions, and more. Traditional rule-based systems may struggle to identify complex anomalies that only become apparent when these disparate data sources are viewed holistically.

How can we connect the dots and identify entities exhibiting suspicious patterns across their entire operational footprint, even if individual activities within a single data source appear normal?

## The Proposed Solution: Unified Profiles & Vector Similarity

This hands-on guide explores a powerful approach leveraging **data fusion**, **machine learning embeddings**, and **vector databases**:

1.  **Data Fusion:** We ingest data from multiple distinct sources.
2.  **Unified Entity Profiles:** We combine information related to a central entity (e.g., a taxpayer) into a single, comprehensive profile, often involving aggregation for one-to-many relationships.
3.  **Vector Embeddings:** We use machine learning techniques (in this MVP, directly using engineered features) to convert each unified profile into a high-dimensional numerical vector, known as an embedding. This embedding captures the essence of the entity's combined characteristics.
4.  **Vector Similarity Search:** We store these embeddings in a specialized **vector database**. This allows us to perform efficient similarity searches – finding entities whose profile embeddings are "closest" (most similar) in the high-dimensional space to a given query profile (e.g., a known fraud example or a profile exhibiting a specific suspicious pattern).

**The Central Idea:** By finding entities that are *similar* based on their *combined cross-source characteristics*, we can uncover potential risks and anomalies that would be invisible when analyzing data sources in isolation.

## MVP Goal and Scope

The goal of this guide is to build a functional MVP that ingests synthetic data representing multiple distinct sources (e.g., tax filings, property records) and uses vector embeddings of unified entity profiles to identify entities similar to known fraud examples or exhibiting suspicious patterns across these combined sources.

Crucially, this MVP uses **synthetic data**. This allows us to control the environment, embed specific cross-source patterns for demonstration, and focus on the core workflow without complexities related to data privacy or access to real-world sensitive information. The aim is to prove the *concept* and provide a practical template.

## Target Audience

This guide is designed for:

* **Data Scientists**
* **Data Analysts**
* **Engineers**

...who are interested in practical applications of data fusion, vector embeddings, and vector databases for solving real-world problems like advanced fraud detection. Basic familiarity with Python, Pandas, and core data science concepts is assumed.

## Guide Structure (Table of Contents)

This guide is structured as a series of Jupyter Notebooks, designed to be run sequentially:

* **[Notebook 00](./notebook_00.ipynb): Environment Setup & Multi-Source Synthetic Data Generation:** Setting up Python, installing libraries, and generating the linkable synthetic datasets with embedded cross-source patterns.
* **[Notebook 01](./notebook_01.ipynb): Source Data Exploration & Initial Cleaning:** Loading and performing initial EDA and cleaning on each individual data source.
* **[Notebook 02](./notebook_02.ipynb): Building Unified Entity Profiles:** Merging sources and aggregating data to create a single profile view per taxpayer.
* **[Notebook 03](./notebook_03.ipynb): Feature Engineering on Unified Profiles:** Creating and selecting relevant features (especially cross-source ones) and preparing them (imputation, encoding, scaling) for embedding.
* **[Notebook 04](./notebook_04.ipynb): Generating Unified Profile Vector Embeddings:** Applying a technique (using engineered features directly) to create a vector embedding for each profile.
* **[Notebook 05](./notebook_05.ipynb): Setting Up Vector DB & Indexing Profile Embeddings:** Initializing a vector database (*ChromaDB* example), creating a collection, and indexing the generated embeddings.
* **[Notebook 06](./notebook_06.ipynb): Querying for Cross-Source Similarity:** Identifying a suspicious query profile and using the vector database to find the N most similar profiles.
* **[Notebook 07](./notebook_07.ipynb): Analyzing Cross-Source Patterns in Similar Profiles:** Validating the query results by examining the original source data for the similar profiles to see if they exhibit the target pattern.
* **[Notebook 08](./notebook_08.ipynb): MVP Summary, Cross-Source Findings, and Next Steps:** Recapping the architecture, discussing findings, limitations, and future directions.

## Technology Stack & The Path to Production Scale

### Example MVP Stack

This guide utilizes a common Python-based stack suitable for data science and MVP development:

* **Core Libraries:** Python, Pandas, NumPy, Scikit-learn
* **Visualization:** Matplotlib, Seaborn
* **Vector Database (MVP Example):** **ChromaDB**
* **Environment:** Jupyter Notebooks

### From MVP to Production: The Scalability Challenge

For this MVP, we are working with a relatively small, synthetically generated dataset (thousands of profiles). For this scale, **ChromaDB** running locally is an excellent choice – it's easy to set up and use, allowing us to focus on the core logic.

However, consider a real-world deployment scenario, for instance, within a country's tax organisation. Such an entity deals with:

* Tens of millions of taxpayers and businesses.
* Billions or trillions of underlying records (tax lines, transactions, property records, etc.) across many years.
* Petabytes, potentially exabytes, of total source data.

If we were to generate embeddings for unified profiles at this scale (tens or hundreds of millions), or especially if we adopted a strategy of embedding more granular source records (potentially leading to billions or trillions of vectors over time), the demands on the vector database become immense. We would require a solution capable of:

* **Massive Scalability:** Handling billions to trillions of vectors and petabytes of associated data.
* **High Performance:** Delivering low-latency similarity searches across this vast dataset.
* **High Ingestion Rates:** Handling continuous updates and additions to the data.
* **Resilience & Efficiency:** Operating reliably and cost-effectively at scale.

While ChromaDB served our MVP well, it is not typically designed for this level of production scale. Transitioning this use case to a production environment necessitates a **massively scalable, enterprise-grade vector database**.

Platforms such as **VAST Data's Vector Database**, integrated within their broader data platform architecture, are specifically designed to provide the **petabyte-scale capacity and high performance** needed to realize the full potential of cross-source similarity analysis on real-world, large-scale datasets like those encountered in national tax authorities or large financial institutions. It represents a key component required to move beyond the MVP and deploy such powerful analytical capabilities effectively in production.


* Tens of millions of taxpayers and businesses (e.g., **~50-100 million** core entities).
* Billions or trillions of underlying records (tax lines, transactions, property records, etc.) across many years.
* Petabytes, potentially exabytes, of total source data.

The demands on the vector database depend heavily on the embedding strategy:

#### Vector Database Size Estimates (Examples)

Let's estimate the potential storage requirements for the vector database itself, assuming a common embedding dimension of **768** using `float32` (4 bytes/dimension) and including a **1.5x-2x overhead** for IDs, metadata, and the search index (e.g., HNSW graph):

1.  **Embedding Granular Records (Medium Scale):**
    * *Scenario:* Embedding billions of individual records (e.g., 100 billion significant records over time).
    * *Raw Vector Size:* 100B vectors * 768 dims * 4 bytes/dim ≈ 307.2 TB (or **~307 TB**).
    * *Estimated DB Size (with overhead):*  ~460 TB to 615 TB. This necessitates a highly scalable, distributed, storage and indexing solution.

3.  **Embedding Granular Records (Large Scale):**
    * *Scenario:* Embedding trillions of individual records (e.g., considering detailed transaction logs over many years).
    * *Raw Vector Size:* 1T vectors * 768 dims * 4 bytes/dim ≈ 3072 TB (or **~3 PB**).
    * *Estimated DB Size (with overhead):* **~4.5 PB to 6 PB**. This is firmly in the **petabyte-scale** domain, demanding specialized infrastructure.

*(Note: These are estimates. Actual size depends on exact vector dimensions, data types, metadata stored, index parameters, and the specific vector database implementation.)*


## How to Use This Guide

Please run the notebooks sequentially, starting from [Notebook 00](./notebook_00.ipynb). Each notebook builds upon the outputs and concepts of the previous ones. Read the Markdown explanations and comments within the code cells to understand the steps involved.

## Let's Get Started!

Proceed to [**Notebook 00**](./notebook_00.ipynb) to begin setting up the environment and generating the synthetic data.
