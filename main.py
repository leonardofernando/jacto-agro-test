import argparse
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

---

Questão: {question}
"""


def main():
    # Busca do usuário
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", action="store", type=str, help="Perguntas e textos para o LLM analisar.")
    args = parser.parse_args()
    query = args.query

    # query = "quais dias ideais para temperatura do milho?"
    # query = "melhor plantar milho, trigo ou arroz esta semana?"
    # query = "quais dias ideais para plantar soja?"

    print(f"Pergunta: {query}\n\n")
    
    # Start ChromaDB
    chroma_db = Chromadb()
    results = chroma_db.query(query_text=query)

    # Criando/formatando contexto
    context = "\n\n----\n\n".join(results)

    # Buscando dados climáticos
    weather_data = WeatherApi().get_weather_data(location="Curitiba", start_date="2025-03-02", end_date="2025-03-09")
    # print(f"{weather_data}\n\n")

    # Gerando prompt para o llm
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.invoke({"context": context, "weather": weather_data, "question": query})
    # print(f"{prompt}\n\n")

    # Chamando llm e passando prompt
    model = OllamaLLM(model="mistral")
    prompt_response = model.invoke(prompt)
    print(f"Resposta: {prompt_response}")


if __name__ == "__main__":
    main()