from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


TEMPLATE = """
Questão: {question}

Resposta: Responda de maneira breve sobre o assunto.
"""

prompt = ChatPromptTemplate.from_template(TEMPLATE)

model = OllamaLLM(model="mistral")

# chain = prompt | model
formatted_prompt = prompt.invoke({"question": "Qual a idade do Issac Newton?"})
print(f"PROMPT: {formatted_prompt}")

ollama_response = model.invoke(formatted_prompt)
print(f"RESPOSTA: {ollama_response}")