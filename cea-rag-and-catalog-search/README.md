# C&A Virtual Assistant with FastAPI, CrewAI and RAG

## Overview
C&A is a global fashion retail company originally founded in the Netherlands in 1841. In Brazil, where this project is inspired, C&A is one of the leading clothing retailers, known for offering affordable fashion for all styles and ages. The company operates both physical stores and an e-commerce platform across the country.

This project is a virtual assistant built using CrewAI, FastAPI, and Retrieval-Augmented Generation (RAG) techniques. It simulates an automated support system for an e-commerce (C&A), capable of:

<p align="center">
<img src="https://www.caruarushopping.com/wp-content/uploads/2019/09/cea.jpg" width=250 height=300>
</p>

- Helping customers find products in the catalog  
- Answering questions based on C&A’s customer service (SAC) policies  
- Performing semantic search using embeddings  
- Storing interaction history in a local SQLite database  

## Features

### 1. Product Search (Catalog)
- Uses the `dados-produtos.json` to perform semantic search based on product titles and descriptions.
- Returns the most similar products with name, price, description, and image.
- Semantic similarity is calculated using the all-MiniLM-L6-v2 model.

### 2. Customer Service Assistant (RAG)
- Uses the `dados-sac.md` document as a source to answer questions related to return, exchange, and policy topics.
- Applies RAG to provide accurate and context-aware responses.

### 3. Interaction Logging
- All user messages and agent responses are logged in a SQLite database (`historico.db`).
- The `/historico` endpoint allows access to this log.

## Project Structure
``` bash
├── main.py # Main API code
├── db/
│ └── historico.db # SQLite database with interaction history
│ └── chroma.sqlite3 # Vector database used on RAG
├── data/
│ ├── dados-produtos.json # Product data for catalog search
│ └── dados-sac.md # Knowledge base for RAG (customer service)
└── .env # Environment variables (API keys)
```

## API Endpoints

- `POST /mensagem`: Sends a message to the agent (`type: "sac"` or `"catalogo"`)
- `GET /historico`: Returns the interaction history with timestamp

## Use Examples

### 1. API RESTful POST RAG (Retrieval-Augmented Generation)
`Scenario 01`
<p align="center">
<img src="https://github.com/user-attachments/assets/109c72fe-8f81-4d36-99d9-5889baea00c7">
</p>

`Scenario 02`
<p align="center">
<img src="https://github.com/user-attachments/assets/26cfd95b-ca12-469c-804e-22f1aab58ecd">
</p>

`Scenario 03`
<p align="center">
<img src="https://github.com/user-attachments/assets/a4b3e130-463a-46b1-83cb-44265246d3d3">
</p>

`Scenario 04`
<p align="center">
<img src="https://github.com/user-attachments/assets/fbae98f4-6643-42c0-8ab5-9a671765ae67">
</p>

### 2. API RESTful POST Product Search (Catalog)
`Scenario 01`
<p align="center">
<img src="https://github.com/user-attachments/assets/715d078e-a803-43e9-8540-43d45e1746f5">
</p>

`Scenario 02`
<p align="center">
<img src="https://github.com/user-attachments/assets/a390ec3a-6d73-4bb0-958d-a6417bb9748a">
</p>

`Scenario 03`
<p align="center">
<img src="https://github.com/user-attachments/assets/bf993a44-8df4-4eab-b243-160bf43a6e9d">
</p>

### 3. API RESTful Get Historical Data
`Scenario 01`
<p align="center">
<img src="https://github.com/user-attachments/assets/66f552d7-cef8-4652-86b2-db6480768f01">
</p>
