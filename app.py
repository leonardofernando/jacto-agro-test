from fastapi import FastAPI, Query
from pydantic import BaseModel
from chroma.chroma_db import Chromadb
from src.weather_api import WeatherApi
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


PROMPT_TEMPLATE = """
Com base nesse contexto de melhor temperatura para plantação:

{context}

---

E com base no clima da semana seguinte:

{weather}

Qual será o resultado da minha safra nessa semana, separado por dia?
"""


app = FastAPI(title="Consulta de dados Agrícolas.", description="API para consulta de dados agrícolas usando RAG.")


class QueryRequest(BaseModel):
    """
    Modelo de requisição para busca de informações no banco de dados vetorial.

    Atributos:
        query (str): Consulta a ser realizada na base de dados.
        top_k (int): Número de resultados mais relevantes a serem retornados.
    """
    query: str
    top_k: int = 3


@app.post("/buscar/", summary="Consulta dados agrícolas com análise de safra.")
def buscar(request: QueryRequest):
    """
    Endpoint para buscar informações no banco de dados vetorial e prever o resultado da safra com base no clima."

    Parâmetros:
        request (QueryRequest): Dados da consulta contendo a query e o número de resultados desejados.

    Retorna:
        dict: Resposta gerada pelo modelo de IA com a previsão da safra.
    """
    chroma_db = Chromadb()
    results = chroma_db.query(query_text=request.query)

    weather_data = WeatherApi().get_weather_data(location="Curitiba", start_date="2025-03-09", end_date="2025-03-09")
    print(f"{weather_data}")

    context = "\n\n----\n\n".join(results)

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.invoke({"context": context, "weather": weather_data})

    model = OllamaLLM(model="mistral")

    prompt_response = model.invoke(prompt)

    return {"prompt_response": prompt_response}


@app.get("/health")
def health_check():
    """
    Endpoint para checar o status de funcionamento da API."

    Retorna:
        dict: Status da API.
    """
    return {"status": "OK"}
