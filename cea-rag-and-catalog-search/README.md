# C&A Virtual Assistant with FastAPI, CrewAI and RAG

**Overview**  
C&A is a global fashion retail company originally founded in the Netherlands in 1841. In Brazil, where this project is inspired, C&A is one of the leading clothing retailers, known for offering affordable fashion for all styles and ages. The company operates both physical stores and an e-commerce platform across the country.

This project is a virtual assistant built using CrewAI, FastAPI, and Retrieval-Augmented Generation (RAG) techniques. It simulates an automated support system for an e-commerce (C&A), capable of:

<p align="center">
<img src="https://www.caruarushopping.com/wp-content/uploads/2019/09/cea.jpg" width=300 height=300>
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
```
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