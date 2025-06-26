# ====================================
# LIBRARIES
from fastapi import FastAPI, Request
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from crewai_tools import RagTool
from crewai.tools import BaseTool
from sentence_transformers import SentenceTransformer, util
from typing import List
import sqlite3
import torch
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# ====================================
# SETUP
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('api_key')
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"
model = os.environ["OPENAI_MODEL_NAME"]

DB_FILE = "db/historico.db"
app = FastAPI()

# ====================================
# SQLITE
def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL, 
            prompt_usuario TEXT NOT NULL,
            resposta_agente TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def log_interaction(prompt, response):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        INSERT INTO interacoes (timestamp, prompt_usuario, resposta_agente)
        VALUES (?, ?, ?)
    """, (timestamp_str, prompt, response))
    conn.commit()
    conn.close()

setup_database()

# ====================================
# TOOLS
# Solution 1: Catalog Search
with open("data/dados-produtos.json", "r", encoding="utf-8") as f:
    produtos = json.load(f)

modelo = SentenceTransformer('all-MiniLM-L6-v2')
corpus = [f"{p['title']} {p['description']}" for p in produtos]
corpus_embeddings = modelo.encode(corpus, convert_to_tensor=True)

class ProductSearchTool(BaseTool):
    name: str = "Busca de Produtos no Catálogo"
    description: str = "Busca produtos no catálogo com base em similaridade semântica."

    def _run(self, query: str) -> str:
        consulta_embedding = modelo.encode(query, convert_to_tensor=True)
        similaridades = util.cos_sim(consulta_embedding, corpus_embeddings)[0]
        top_indices = torch.topk(similaridades, k=5).indices
        resultados = [produtos[i] for i in top_indices if similaridades[i] > 0.4]

        if not resultados:
            return "❌ Nenhum produto encontrado."

        resposta = ""
        for p in resultados:
            resposta += (
                f"\n🛍️ *{p['title']}*\n"
                f"💲 R$ {p['price']:.2f}\n"
                f"📄 {p['description']}\n"
                f"🖼️ {p['image']}\n"
            )
        return resposta.strip()

catalogo_tool = ProductSearchTool()

# Solution 2: RAG
knowledge_base = RagTool(
    rag_name="Busca em assuntos de SAC",
    docs=['data/dados-sac.md'],
    description="Uma ferramenta para buscar informações específicas dentro do documento de SAC da C&A para tratar de assuntos de políticas de troca, devolução etc.",
    config={
    "vectordb": {
        "config": {
            "dir": "db",  # Specify custom database directory
        }
    }
})

# ====================================
# AGENTS
# Solution 1: Catalog Search
agente_catalogo = Agent(
    role="Especialista de Catálogo de Produtos",
    goal="Ajudar o cliente a encontrar produtos desejados.",
    backstory="Especialista em produtos da C&A.",
    tools=[catalogo_tool],
    allow_delegation=False,
    verbose=True,
    llm=model
)

tarefa_catalogo = Task(
    description="Cliente procura produto: '{busca}'",
    expected_output="Lista de produtos com nome, preço, descrição e imagem.",
    agent=agente_catalogo
)

crew_catalogo = Crew(
    agents=[agente_catalogo],
    tasks=[tarefa_catalogo],
    process=Process.sequential
)

# Solution 2: RAG
agente_sac = Agent(
    role='Especialista SAC',
    goal='Responder com base nas políticas de SAC da C&A.',
    backstory='Você é um assistente experiente no SAC da C&A.',
    tools=[knowledge_base],
    allow_delegation=False,
    llm=model
)

tarefa_sac = Task(
    description="Cliente quer saber sobre: '{topic}'",
    expected_output='Resposta com base nas políticas da empresa.',
    agent=agente_sac
)

crew_sac = Crew(
    agents=[agente_sac],
    tasks=[tarefa_sac],
    process=Process.sequential
)

# ====================================
# ENDPOINTS
class MensagemRequest(BaseModel):
    tipo: str  # "sac" ou "catalogo"
    texto: str

@app.post("/mensagem")
def enviar_mensagem(mensagem: MensagemRequest):
    if mensagem.tipo == "catalogo":
        resposta = crew_catalogo.kickoff(inputs={"busca": mensagem.texto})
    elif mensagem.tipo == "sac":
        resposta = crew_sac.kickoff(inputs={"topic": mensagem.texto})
    else:
        return {"erro": "Tipo inválido. Use 'sac' ou 'catalogo'."}

    log_interaction(mensagem.texto, str(resposta))
    return {"resposta": str(resposta)}

@app.get("/historico")
def get_historico():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, prompt_usuario, resposta_agente FROM interacoes ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    historico = [
        {"id": r[0], "timestamp": r[1], "usuario": r[2], "agente": r[3]}
        for r in rows
    ]
    return historico