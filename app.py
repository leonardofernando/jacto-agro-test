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


app = FastAPI(title="Consulta de dados Agrícolas.", description="chaisa")


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


@app.post("/buscar/", summary="bla bla bla")
def buscar(request: QueryRequest):
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
    return {"status": "OK"}
