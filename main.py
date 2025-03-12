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
    """
    Função principal que executa a consulta de dados agrícolas.
    
    - Recebe uma pergunta via argumento de linha de comando.
    - Busca informações relacionadas no banco de vetores (ChromaDB).
    - Obtém dados climáticos da API de clima.
    - Constrói um prompt e consulta um modelo de linguagem para obter insights agrícolas.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", action="store", type=str, help="Perguntas e textos para o LLM analisar.")
    args = parser.parse_args()
    query = args.query

    # query = "quais dias ideais para temperatura do milho?"
    # query = "melhor plantar milho, trigo ou arroz esta semana?"
    # query = "quais dias ideais para plantar soja?"

    print(f"Pergunta: {query}\n\n")
    
    chroma_db = Chromadb()
    results = chroma_db.query(query_text=query)

    context = "\n\n----\n\n".join(results)

    weather_data = WeatherApi().get_weather_data(location="Curitiba", start_date="2025-03-02", end_date="2025-03-09")

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.invoke({"context": context, "weather": weather_data, "question": query})

    model = OllamaLLM(model="mistral")
    prompt_response = model.invoke(prompt)
    print(f"Resposta: {prompt_response}")


if __name__ == "__main__":
    main()