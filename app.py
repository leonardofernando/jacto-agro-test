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

PROMPT_TEMPLATE_TEST = """
Questão: {question}

Resposta: Responda de maneira breve sobre o assunto."""


app = FastAPI(title="Consulta de dados Agrícolas.")


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


@app.post("/buscar/")
def buscar(request: QueryRequest):
    # bot especialista, 1 semana por exemplo
    chroma_db = Chromadb()
    print("Start ChromaDB")
    results = chroma_db.query(query_text=request.query)

    # busca api
    weather_data = WeatherApi().get_weather_data(location="Curitiba", start_date="2025-03-09", end_date="2025-03-09")
    print(f"{weather_data}")

    context = "\n\n----\n\n".join(results)

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.invoke({"context": context, "weather": weather_data})
    print(f"{prompt}")
    # prompt = prompt_template.invoke({"question": "1 + 1 = 3? ou existe outro resultado?"})

    model = OllamaLLM(model="mistral")

    prompt_response = model.invoke(prompt)

    return {"prompt_response": prompt_response}


@app.get("/health")
def health_check():
    return {"status": "OK"}
